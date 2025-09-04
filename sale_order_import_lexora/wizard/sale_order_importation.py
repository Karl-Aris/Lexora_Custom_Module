from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
import datetime
import xlrd
import base64

from pandas.tseries.api import guess_datetime_format
import re


class SaleOrderImportation(models.TransientModel):
    _name = "sale.order.importation"
    _description = "Sale Order Importation"

    attachment = fields.Binary(string="File", required=True)
    header_ids = fields.One2many('sale.order.importation.header', 'importation_id')
    is_header_invalid = fields.Boolean(default=False)
    invalid_headers_warning = fields.Html(store=False)
    header_guidelines_display = fields.Html(default=lambda self: self._compute_header_guidelines(), store=False)
    mode = fields.Selection([('csv','CSV'),('xlsx','XLSX')],string="File type", default='xlsx')
    template_id = fields.Many2one('lexora.so.import.template', string="Template")

    def action_upload(self):
        recordsets, invalid_data = self.start_upload()
        return self.upload_notify(recordsets, invalid_data)

    def upload_notify(self, recordsets, invalid_data):
        upload_id = self.env['sale.order.upload.result'].create({
            "name": "%s" % (
                datetime.datetime.utcnow(
                    ).strftime("%h/%d/%Y %H:%M:%S")
            ),
            "attachment": self.attachment,
        })
        if recordsets:
            upload_id.write({
                "order_ids": [(6, 0, recordsets.ids)],
            })
        if invalid_data:
            upload_id.write({
                "invalid_ids": [
                    (0, 0, {
                        "name": data.get("row"),
                        "column": data.get("column"),
                        "value": data.get("value"),
                        "upload_id": upload_id.id
                    })
                    for data in invalid_data
                ],
            })

        action = self.env.ref('sale_order_import_lexora.action_sale_order_upload_result_form')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('%s order/s imported' % len(recordsets)),
                'message': '%s',
                'links': [{
                    'label': "View details",
                    'url': f'#action={action.id}&id={upload_id.id}&model={upload_id._name}'
                }],
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    @api.onchange('attachment')
    def _onchange_attachment(self):
        if self.attachment:
            self._check_headers()

    def _open_workbook(self):
        attachment = base64.b64decode(self.attachment)
        
        #determine if attachment is csv or excel file
        try:
            csv_content = attachment.decode('utf-8')
        except:
            csv_content = ''

        # Open the Excel file using xlrd
        try:
            workbook = xlrd.open_workbook(file_contents=attachment)
        except:
            workbook = ''
        return workbook, csv_content

    def _check_headers(self):
        workbook,csv_content = self._open_workbook()
        if workbook:
            worksheet = workbook.sheet_by_index(0)
            sheet_header = worksheet.row_values(0)
            default_headers = self._get_headers()
            default_header_vals = [list(header.values())[0] for header in self._get_headers()]
    
            invalid_headers = []
            for header in sheet_header:
                if header not in default_header_vals:
                    invalid_headers.append(header)
    
            if invalid_headers:
                self.invalid_headers_warning = (
                    "Invalid column header(s): <strong>%s</strong>."
                    % ", ".join(invalid_headers)
                )
                self.is_header_invalid = True
            else:
                self.is_header_invalid = False
    
            # def _import_config_compute(header):
            #     header_id = self.env['sale.order.importation.header.config'].search([("name", "ilike", header)], limit=1)
            #     return header_id
    
            # self.header_ids = [Command.clear()] + [
            #     (0, 0, {
            #         'name': _import_config_compute(header_name).name,
            #         'technical_name': _import_config_compute(header_name).field_technical_name,
            #         'importation_id': ([6, 0, self.ids]),
            #         'is_required': _import_config_compute(header_name).is_required,
            #     })
            #     for header_name in sheet_header
            # ]
        elif csv_content:
            pass

    def _set_attrib(self, obj, field, value):
        if obj.exists():
            setattr(obj, field, value)
        else:
            obj = obj.search([("name", '=ilike', value)], limit=1)
            if not obj.exists():
                obj = obj.create({"name": value})
        return obj

    def po_exists(self, po):
        po_id = self.env['sale.order'].search([("purchase_order", "=", po)], limit=1)
        if not po_id.exists() and isinstance(po, float):
            po = int(po)
            po_id = po_id.search([("purchase_order", "=", po)], limit=1)
        return po_id.exists()

    def _get_headers(self):
        headers = [
            {"order_state": "Order State"},
            {"purchase_order": "PO"},
            {"date_order": "Order Date"},
            {"order_process_date": "Order Process Date"},
            {"partner_id": "Merchant"},
            {"order_customer": "Customer"},
            {"order_address": "Address"},
            {"order_phone": "Phone"},
            {"order_line|default_code": "SKU"},
            {"order_line|product_uom_qty": "Quantity"},
            {"order_line|price_unit": "Price"},
            {"carrier_id|name": "Carrier"},
            {"carrier_id|amount": "Shipping Quote"},
            {"carrier_id|mode_freight": "Mode or Freightview"},
            {"picking_ids|carrier_tracking_ref": "Tracking number"},
            {"picking_ids|dimension": "Dimensions"},
            {"picking_ids|missing_parts": "Shuffles and Missing Parts"},
            {"picking_ids|note": "Notes"},
            {"added_by": "Initials/ Added by"},
        ]
        return headers

    def _header_help(self):
        data = {
            "order_state": {
                "required": True,
                "input": "Char",
                "choices": self._get_valid_order_state(),
                "help_txt": "The current state of the order, such as 'po' (initial state), 'processed', 'shipped' or 'cancelled'.",
                "column": "Order State"
            },
            "purchase_order": {
                "required": True,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The unique identifier for the order.",
                "column": "PO"
            },
            "date_order": {
                "required": True,
                "input": "Date",
                "choices": "N/A",
                "help_txt": "The date when the order was placed, formatted as MM/DD/YYYY.",
                "column": "Order Date"
            },
            "order_process_date": {
                "required": False,
                "input": "Date",
                "choices": "N/A",
                "help_txt": "The date when the order is processed, formatted as MM/DD/YYYY. Leave empty if not applicable.",
                "column": "Order Process Date"
            },
            "partner_id": {
                "required": True,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The merchant or dealer associated with the order.",
                "column": "Merchant"
            },
            "order_customer": {
                "required": True,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The name of the customer who placed the order.",
                "column": "Customer"
            },
            "order_address": {
                "required": True,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The shipping address for the order.",
                "column": "Address"
            },
            "order_phone": {
                "required": False,
                "input": "Number",
                "choices": "N/A",
                "help_txt": "The phone number associated with the order. This field is optional.",
                "column": "Phone"
            },
            "order_line|default_code": {
                "required": True,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The default code/ SKU of the product item in the order.<br/> Use '/' (forward slash) to separate multiple SKUs.",
                "column": "SKU"
            },
            "order_line|product_uom_qty": {
                "required": True,
                "input": "Number",
                "choices": "N/A",
                "help_txt": "The quantity of the product ordered.<br/> Use '\\' (back slash) to separate multiple quantities.",
                "column": "Quantity"
            },
            "order_line|price_unit": {
                "required": True,
                "input": "Amount",
                "choices": "N/A",
                "help_txt": "The unit price of the product.<br/> Use '/' (forward slash) to separate multiple unit prices.",
                "column": "Price"
            },
            "carrier_id|name": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The name of the carrier responsible for delivering the order. Optional field.",
                "column": "Carrier"
            },
            "carrier_id|amount": {
                "required": False,
                "input": "Amount",
                "choices": "N/A",
                "help_txt": "The cost associated with the carrier for shipping. Optional field.",
                "column": "Shipping Quote"
            },
            "carrier_id|mode_freight": {
                "required": False,
                "input": "Char",
                "choices": ["Mode", "Freightview"],
                "help_txt": "Values are 'Mode' or 'Freightview'. Optional field.",
                "column": "Mode or Freightview"
            },
            "picking_ids|carrier_tracking_ref": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The tracking reference provided by the carrier for the shipment. Optional field.",
                "column": "Tracking number"
            },
            "picking_ids|dimension": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The dimensions of the package, typically including length, width, and height. Optional field.",
                "column": "Dimensions"
            },
            "picking_ids|missing_parts": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "Details of any missing parts or items from the shipment. Optional field.",
                "column": "Shuffles and Missing Parts"
            },
            "picking_ids|note": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "Any additional notes or comments regarding the picking process. Optional field.",
                "column": "Notes"
            },
            "added_by": {
                "required": False,
                "input": "Char",
                "choices": "N/A",
                "help_txt": "The name or identifier of the person who added the order or information. Optional field.",
                "column": "Initials/ Added by"
            }
        }

        return data

    def _compute_header_guidelines(self):
        headers_help = self._header_help()
        default_headers = self._get_headers()
        default_header_keys = [list(header.keys())[0] for header in default_headers]
        guide_tbl = (
            "<div class=''>"
            + "<table class='o_list_table table table-sm table-hover position-relative mb-0 o_list_table_ungrouped table-striped'>"
            + "<thead>"
            + "<tr>"
            + "<th class='o_list_record_selector o_list_controller align-middle pe-1 cursor-pointer'>"
            + "Column"
            + "</th>"
            + "<th class='o_list_record_selector o_list_controller align-middle pe-1 cursor-pointer'>"
            + "Description"
            + "</th>"
            + "<th class='o_list_record_selector o_list_controller align-middle pe-1 cursor-pointer'>"
            + "Choices"
            + "</th>"
            + "<th class='o_list_record_selector o_list_controller align-middle pe-1 cursor-pointer'>"
            + "Required"
            + "</th>"
            + "<th class='o_list_record_selector o_list_controller align-middle pe-1 cursor-pointer'>"
            + "Input"
            + "</th>"
            + "</tr>"
            + "</thead>"
            + "<tbody>"
            + "{tbl_data}"
            + "</tbody>"
            + "</table>"
            + "</div>"
        )
        tbl_data = ""
        for header in default_header_keys:
            data = headers_help.get(header)
            if data:
                tbl_row = (
                    "<tr>"
                    + "<td class='o_data_cell cursor-pointer o_field_cell o_list_char  o_readonly_modifier fw-bold'> %s </td>" % data.get("column")
                    + "<td> %s </td>" % data.get("help_txt")
                    + "<td> %s </td>" % data.get("choices")
                    + "<td> %s </td>" %  (u'\u2713' if data.get("required") else "")
                    + "<td> %s </td>" % data.get("input")
                    + "</tr>"
                )
                tbl_data += tbl_row
        return guide_tbl.format(tbl_data=tbl_data)

    def _get_require_col(self):
        return [0, 1, 2, 4, 5, 6, 8, 9, 10]

    def _get_valid_order_state(self):
        return ["po", "shipped", "processed", "cancelled"]

    def _get_partner_id(self, name):
        partner_id = self.env['res.partner'].search([("name", '=ilike', name)], limit=1)
        if not partner_id.exists():
            partner_id = partner_id.create({"name": name})
        return partner_id

    def _get_product_id(self, sku, row_index):
        PRODUCT = self.env['product.product']
        product_id = PRODUCT.search([("default_code", "=", sku)], limit=1)
        if not product_id.exists():
            raise UserError(
                "Product SKU [%s] at [row %s] not found, please check your input before importing."
                % (sku, row_index)
            )
        return product_id

    def _get_carrier_id(self, name):
        product_temp_id = self.env['product.template']
        carrier_id = self.env['delivery.carrier']

        product_temp_id = product_temp_id.search(
            [("name", "ilike", "Standard delivery")],
            limit=1
        )
        if not product_temp_id.exists():
            product_temp_id = product_temp_id.create({"name": "Standard delivery"})

        carrier_id = carrier_id.search([
            ("name", "ilike", name)
        ], limit=1)
        if not carrier_id.exists():
            carrier_id = carrier_id.create(
                {"name": name, "product_id": product_temp_id.id}
            )

        return carrier_id

    def start_upload(self):
        workbook, csv_content = self._open_workbook()
        # file_row_index = [
        #     'po state',
        #     'po ref',
        #     'po date1',
        #     'po date2',
        #     'merchant',
        #     'customer',
        #     'customer address',
        #     'customer phone',
        #     'sku',
        #     'sku qty',
        #     'sku price',
        #     'sku courier',
        #     'sku courier quote',
        #     'sku courier mode',
        #     'tracking number',
        #     'dimension',
        #     'shuffles',
        #     'notes',
        #     'salesman',
        #     ]        
        if workbook:
            worksheet = workbook.sheet_by_index(0)
            # sheet_header = worksheet.row_values(0) # variable unused
        
        def _push_invalid(column, row, error_msg):
            inv_data = {
                "column": column,
                "value": error_msg,
                "row": row_index,
            }
            invalid_row = True
            return inv_data, invalid_row

        def _push_post_action(rel_field, base_field, cell_value, post_action_row):
            if rel_field in post_action_row:
                post_action_row[rel_field].update({base_field: cell_value})
            else:
                post_action_row.update({rel_field: {base_field: cell_value}})

        to_upload = []
        post_actions = []
        invalid_data = []
        required_so_template_data_list = []
        mode = self.mode
        template_data_info_list = []
        
        
        if mode == 'xlsx' and not self.template_id: # for xls  
            iterate_base = range(1, worksheet.nrows)

        else: # for csv
            
            #fetch information to the related template data
            template_data_info_list = self.template_id.template_data_ids.read(['sequence','data_id'])            
            
            iterate_base = range(self.template_id.data_row_start - 1, len(csv_content.split('\n')) - 2)
            required_so_template_data_list = [x.required for x in self.template_id.template_data_ids]
            
            so_field_model_dict = dict([(x.name,x.relation) for x in self.env['ir.model'].search([('model','=','sale.order')]).field_id if '_id' in x.name])
            
            mode_header_base = [
                    ('PO', 'lexora_sale_order_importation_template_data_po_ref','purchase_order'),
                    ('PO State', 'lexora_sale_order_importation_template_data_po_state','order_state'),
                    ('Order Date1', 'lexora_sale_order_importation_template_data_po_date1','date_order'),
                    ('Order Date2', 'lexora_sale_order_importation_template_data_po_date2','order_process_date'),
                    ('Merchant', 'lexora_sale_order_importation_template_data_merchant','partner_id'),
                    ('Customer Name', 'lexora_sale_order_importation_template_data_customer','order_customer'),
                    ('Customer Address', 'lexora_sale_order_importation_template_data_customer_address','order_address'),
                    ('Customer Phone', 'lexora_sale_order_importation_template_data_customer_phone','order_phone'),
                    ('SKU', 'lexora_sale_order_importation_template_data_sku','order_line|default_code'),
                    ('SKU Qty', 'lexora_sale_order_importation_template_data_sku_qty','order_line|product_uom_qty'),
                    ('SKU Price', 'lexora_sale_order_importation_template_data_sku_price','order_line|price_unit'),
                    ('SKU Currency', 'lexora_sale_order_importation_template_data_currency','currency_id'),
                    ('Courier', 'lexora_sale_order_importation_template_data_sku_courier','carrier_id|name'),
                    ('Shipping Quote', 'lexora_sale_order_importation_template_data_sku_courier_quote','carrier_id|amount'),
                    ('Courier Mode', 'lexora_sale_order_importation_template_data_sku_courier_mode','carrier_id|mode_freight'),
                    ('Tracking Number', 'lexora_sale_order_importation_template_data_tracking_number','picking_ids|carrier_tracking_ref'),
                    ('Dimension', 'lexora_sale_order_importation_template_data_dimension','picking_ids|dimension'),
                    ('Shuffles', 'lexora_sale_order_importation_template_data_shuffles','picking_ids|missing_parts'),
                    ('Notes', 'lexora_sale_order_importation_template_data_notes','picking_ids|note'),
                    #--------------
                    ('Customer Address City','lexora_sale_order_importation_template_data_customer_address_city','partner_id|city'),
                    ('Customer Address Country','lexora_sale_order_importation_template_data_customer_address_country','partner_id|country_id'),
                    ('Customer Address Postal Code','lexora_sale_order_importation_template_data_customer_address_postal_code','partner_id|zip'),
                    ('Customer Address State','lexora_sale_order_importation_template_data_customer_address_state','partner_id|state_id'),
                    ('Customer Address 1','lexora_sale_order_importation_template_data_customer_address_1','partner_id|street'),
                    ('Customer Address 2','lexora_sale_order_importation_template_data_customer_address_2','partner_id|street2'),
                    ('Dealer SKU','lexora_sale_order_importation_template_data_dealers_sku','order_line|product_id|product_dealer_sku_ids'),
                ]
            mode_header_conversion = {x : (self.env.ref('sale_order_import_lexora.%s' % y).id, z) for x,y,z in mode_header_base}
            #example: {'PO':(3, 'purchase_order')}    


        for row_index in iterate_base:  # Skip the header row
            # invalid_row = False
            row_record = {}
            post_action_row = {}
            cell_value = False
            product_id = self.env['product.product']
            csv_customer_address = []
            #post_action_row[rel_field: {base_field: cell_value}
            #example: post_action_row['order_line']:{'price_unit': 100.00}            
            
            # row_actions = {
            #     "state_action": [],
            #     "warehouse_action": [],
            #     "product_action": [],
            #     "delivery_action": [],
            # }
            # merchant_id = self.env['res.partner']
            customer_id = self.env['res.partner']
            # product_temp_ids = self.env['sale.order.line']
            # picking_ids = self.env['stock.picking']
            

            if mode == 'xlsx' and not self.template_id: # for xls
                row_enumerate = enumerate(worksheet.row_values(row_index))
            else: # for csv
                #row_enumerate = enumerate(csv_content.split('\n')[row_index].split(','))
                pattern = r'(?:[^,"]|"(?:\\.|[^"])*")+' 
                temp = re.findall(pattern, csv_content.split('\n')[row_index])
                row_enumerate = enumerate(temp) 

            for i, cell_value in row_enumerate:

                #remove quotes in value
                cell_value = ''.join([x for x in cell_value if x not in ('"',"'")])
                
                if cell_value == "N/A":
                    cell_value = ''
                key_col = ''
                data_ref_id = False
                if template_data_info_list:
                    data_ref_id = template_data_info_list[i].get('data_id',[0,0])[0]

                post_action_cell = False
               
                if mode == 'xlsx':
                    current_header = list(self._get_headers()[i].items())[0]
                
                #key_col reference for data insertion
                
                if mode == 'xlsx':
                    key_col, current_col = current_header
                elif mode == 'csv':
                    for temp_col in mode_header_conversion:
                        if mode_header_conversion[temp_col][0] == data_ref_id:
                            current_col = temp_col
                            key_col = mode_header_conversion[temp_col][1]
                            break
                    #handling other related field (_id)
                    #native to sale_order
                    if '_id' in key_col and key_col in so_field_model_dict:
                        target_model_name = so_field_model_dict[key_col]
                        try:
                            cell_value = self.env[target_model_name].search([('name','=',cell_value)])[0].id
                        except:
                            pass
                # if i >= 11:
                #     print(i,current_col)
                #     pass
                        
                # checking column if required
                required_error_msg = "Column is required"
                if mode == 'csv' and self.template_id:
                    if required_so_template_data_list[i] and not cell_value:
                        invalid_data.append({'column': self.template_id.template_data_ids[i].data_id.display_name, #data name
                                             'value': required_error_msg,
                                             'row': i,})

                if i in self._get_require_col() and not cell_value:
                    inv_data, is_invalid = _push_invalid(current_col, row_index, required_error_msg )
                    invalid_data.append(inv_data)
                    # invalid_row = is_invalid
                
                #handling PO data    
                # Order State
                if (mode == 'xlsx' and i in [0]) \
                     or (mode == 'csv' and mode_header_conversion['PO State'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'PO State'
                    #     key_col = mode_header_conversion[current_col][1]
                    if cell_value.lower() in self._get_valid_order_state():
                        cell_value = cell_value.lower().replace("led", "").replace("ped", "").replace("ed", "")
                    elif mode == 'csv':
                        target_platforms = ['Houzz']
                        if self.template_id and self.template_id.display_name in target_platforms:
                            if cell_value == 'Charged':
                                cell_value = 'po'
                                
                    else:
                        inv_data, is_invalid = _push_invalid(current_col, row_index, "Invalid Order State")
                        invalid_data.append(inv_data)
                        # invalid_row = is_invalid

                    _push_post_action(key_col, key_col, cell_value, post_action_row)

                # PO
                elif (mode == 'xlsx' and i in [1]) \
                    or (mode == 'csv' and mode_header_conversion['PO'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'PO'
                    #     key_col = mode_header_conversion[current_col][1]
                    if self.po_exists(cell_value):
                        inv_data, is_invalid = _push_invalid(current_col, row_index, "PO already exists")
                        invalid_data.append(inv_data)
                        # invalid_row = is_invalid
                        break
                    else:
                        if isinstance(cell_value, float):
                            cell_value = int(cell_value)

                # Order Date/ Order Process Date
                elif (mode == 'xlsx' and i in [2, 3]) \
                    or (mode == 'csv' and (mode_header_conversion['Order Date1'][0] == data_ref_id \
                        or mode_header_conversion['Order Date2'] == data_ref_id)):
                    # if mode == 'csv':
                    #     current_col = 'Order Date2'
                    #     key_col = mode_header_conversion[current_col][1]
                    if cell_value and isinstance(cell_value,str):          
                        #remove quetos in date value
                        guessed_date_format = guess_datetime_format(cell_value)
                        cell_value = datetime.datetime.strptime(cell_value, guessed_date_format)
                    

                # Merchant
                elif (mode == 'xlsx' and i in [4]):# \
                    # or (mode == 'csv' and mode_header_conversion['Merchant'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Merchant'
                    #     key_col = mode_header_conversion[current_col][1]
                    cell_value = self._get_partner_id(cell_value).id

                # Customer Name
                elif (mode == 'xlsx' and i in [5] and not cell_value) \
                    or (mode == 'csv' and mode_header_conversion['Customer Name'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Customer Name'
                    #     key_col = mode_header_conversion[current_col][1]
                    
                        customer_id = self._get_partner_id(cell_value)
                        #code will break if customer data if this is not referred before other customer data
                      
                        cell_value = customer_id.name
                    

                # Customer Address
                ## customer name needs to be processed first for this to work
                elif (mode == 'xlsx' and  i in [6] and not cell_value) \
                    or (mode == 'csv' and (mode_header_conversion['Customer Address'][0] == data_ref_id \
                                           or mode_header_conversion['Customer Address 1'][0] == data_ref_id \
                                           or mode_header_conversion['Customer Address 2'][0] == data_ref_id)):
                    # if mode == 'csv':
                    #     current_col = 'Customer Address'
                    #     key_col = mode_header_conversion[current_col][1]
                    
                    # if customer_id.partner_id:
                    #     cell_value = customer_id.partner_id.contact_address_complete
                    # else:
                    # customer_id.street = cell_value
                    if mode == 'xlsx':
                        cell_value = customer_id.partner_id.contact_address_complete
                    elif mode == 'csv':
                        csv_customer_address.append(cell_value)
                        post_action_cell = True

                # Customer Phone
                ## customer name needs to be processed first for this to work
                elif (mode == 'xlsx' and i in [7]) \
                    or (mode == 'csv' and mode_header_conversion['Customer Phone'][0] == data_ref_id):
                    
                    # if mode == 'csv':
                    #     current_col = 'Customer Phone'
                    #     key_col = mode_header_conversion[current_col][1]
                    if not cell_value:
                        cell_value = customer_id.phone
                    else:
                        customer_id.phone = cell_value
                    if isinstance(cell_value, float):
                        cell_value = int(cell_value)

                # ORDER LINES #
                # SKU -- Post action field
                elif (mode == 'xlsx' and i in [8]) \
                    or (mode == 'csv' and mode_header_conversion['SKU'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'SKU'
                    #     key_col = mode_header_conversion[current_col][1]
                    cell_values = [cell_value]
                    if "/" in cell_value:
                        cell_values = cell_value.replace(" ", "").split("/")

                    cell_value_ids = []
                    for cell_value in cell_values:
                        product_id = self._get_product_id(cell_value, row_index).id
                        cell_value = product_id
                        cell_value_ids.append(cell_value)

                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, "product_id", cell_value_ids, post_action_row)
                    post_action_cell = True

                # Quantity -- Post action field
                elif (mode == 'xlsx' and i in [9]) \
                    or (mode == 'csv' and mode_header_conversion['SKU Qty'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'SKU Qty'
                    #     key_col = mode_header_conversion[current_col][1]
                    cell_values = [cell_value]
                    if not isinstance(cell_value, float) and "\\" in cell_value:
                        cell_values = cell_value.replace(" ", "").split("\\")

                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_values, post_action_row)
                    post_action_cell = True

                # Price -- Post action field
                elif (mode == 'xlsx' and i in [10]) \
                    or (mode == 'csv' and mode_header_conversion['SKU Price'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'SKU Price'
                    #     key_col = mode_header_conversion[current_col][1]
                    # should add after the creation of SO
                    cell_values = [cell_value]
                    if not isinstance(cell_value, float) and "/" in cell_value:
                        cell_values = cell_value.replace(" ", "").split("/")

                    cell_value_ids = []
                    for cell_value in cell_values:
                        if not isinstance(cell_value, float):
                            cell_value = cell_value.replace("$", "").replace(",", "")
                        cell_value_ids.append(cell_value)
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value_ids, post_action_row)
                    post_action_cell = True

                # SHIPPING #
                # Carrier -- Post action field
                elif (mode == 'xlsx' and i in [11]) \
                    or (mode == 'csv' and mode_header_conversion['Courier'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Courier'
                    #     key_col = mode_header_conversion[current_col][1]
                    cell_value = self._get_carrier_id(cell_value).id

                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, "carrier_id", cell_value, post_action_row)
                    post_action_cell = True

                # Shipping Quote -- Post action field
                elif (mode == 'xlsx' and i in [12]) \
                    or (mode == 'csv' and mode_header_conversion['Shipping Quote'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Shipping Quote'
                    #     key_col = mode_header_conversion[current_col][1]
                    if not isinstance(cell_value, float):
                        cell_value = cell_value.replace("$", "").replace(",", "")
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True

                # Mode or Freightview -- Post action field
                elif (mode == 'xlsx' and i in [13]) \
                    or (mode == 'csv' and mode_header_conversion['Courier Mode'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Courier Mode'
                    #     key_col = mode_header_conversion[current_col][1]
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True

                # Warehouse| Pickings #
                # Tracking Number -- Post action field
                elif (mode == 'xlsx' and i in [14]) \
                    or (mode == 'csv' and mode_header_conversion['Tracking Number'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Tracking Number'
                    #     key_col = mode_header_conversion[current_col][1]
                    rel_field, base_field = key_col.split("|")

                    if isinstance(cell_value, float):
                        cell_value = int(cell_value)    

                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True

                # Dimensions -- Post action field
                elif (mode == 'xlsx' and i in [15]) \
                    or (mode == 'csv' and mode_header_conversion['Dimension'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Dimension'
                    #     key_col = mode_header_conversion[current_col][1]
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True

                # Shuffles... -- Post action field
                elif (mode == 'xlsx' and i in [16]) \
                    or (mode == 'csv' and mode_header_conversion['Shuffles'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Shuffles'
                    #     key_col = mode_header_conversion[current_col][1]
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True

                # Notes -- Post action field
                elif (mode == 'xlsx' and i in [17]) \
                    or (mode == 'csv' and mode_header_conversion['Notes'][0] == data_ref_id):
                    # if mode == 'csv':
                    #     current_col = 'Notes'
                    #     key_col = mode_header_conversion[current_col][1]
                    rel_field, base_field = key_col.split("|")
                    _push_post_action(rel_field, base_field, cell_value, post_action_row)
                    post_action_cell = True
                    
                #handles other headers
                else:
                    if mode == 'csv':
                        #fetch related field
                        for temp_label in mode_header_conversion:
                            temp_data = mode_header_conversion[temp_label] 
                            if temp_data[0] == data_ref_id:
                                key_col = temp_data[1]
                                if '|' in key_col:
                                    
                                    #handles dealer sku
                                    if current_col == 'Dealer SKU':
                                        if not product_id and cell_value:
                                        
                                            #search dealer sku
                                            search_arg = [('default_code','=',cell_value)]
                                            temp_res = self.env['product.product'].search_read(search_arg,['id'])
                                            if temp_res:
                                                cell_value_ids = [x['id'] for x in temp_res]
                                                
                                                _push_post_action('order_line', "product_id", cell_value_ids, post_action_row)
                                        post_action_cell = True
                                    
                                    #handles customer data
                                    elif 'partner_id' == key_col.split('|')[0] and customer_id:
                                        rel_field, base_field = key_col.split("|")
                                        
                                        if '_id' in base_field:
                                            # COUNTRY
                                            if base_field == 'country_id' \
                                                and cell_value in ('US','USA') :
                                                    cell_value = self.env.ref('base.us').id
                                            # STATE
                                            elif base_field == 'state_id':
                                                #assumes state code is used
                                                if len(cell_value) <= 6:
                                                    search_arg = [('code','=',cell_value)]
                                                    
                                                else:
                                                    search_arg = [('name','ilike',cell_value)]
                                                search_res = self.env['res.country.state'].search(search_arg)
                                                if not search_res:
                                                    for temp_value in cell_value.split(' '):
                                                        search_arg = [('name','ilike',temp_value)]
                                                        temp_res = self.env['res.country.state'].search(search_arg)
                                                        if temp_res:
                                                            search_res = temp_res
                                                            break
                                                if not search_res: 
                                                    raise UserError("State (%s) can't be determined!" % cell_value)
                                                    
                                                cell_value = search_res[0].id
                                                        
                                            else:    
                                                target_model_name = customer_id.fields_get(base_field)[base_field]['relation']
                                                temp_val = self.env[target_model_name].search([('name','ilike',cell_value)])
                                                if temp_val:
                                                    cell_value = temp_val[0].id
                                                else:
                                                    cell_value = []
                                        
                                        

                                        customer_id.write({base_field:cell_value})
                                        post_action_cell = True
                                break

                if post_action_cell or not key_col:
                    continue
                row_record[key_col] = cell_value
            #CSV : generates value for 'order_address'
            if not row_record.get('order_address', False) and csv_customer_address:
                row_record['order_address'] = ' '.join([x.replace('N/A','') for x in csv_customer_address])
            
            to_upload.append(row_record)
            post_actions.append(post_action_row)

        if to_upload:
            recordsets = self._create_orders(to_upload, post_actions)

        try:
            return recordsets, invalid_data
        except UnboundLocalError:
            raise UserError("Please upload a file that contains valid data. Ensure the file is not empty and try again.")

        
    def _create_orders(self, data, actions):
        # Since PO is required and unique, record shouldnt be created
        # If no PO is present in data
        data = [item for item in data if item.get("purchase_order")]
        recordsets = self.env['sale.order'].create(data)

        carrier_id = self.env['delivery.carrier']
        wizard_carrier_id = self.env['choose.delivery.carrier']

        for i, record in enumerate(recordsets):
            updates = {}
            order_state = "po"
            warehouse_updates = {}
            product_items = []
            product_items_count = 0
            for key, value in actions[i].items():

                # Shipment Action
                if "carrier_id" in key:
                    carrier_id = carrier_id.browse(value.get("carrier_id"))
                    carrier_id.write({})
                    wizard_carrier_id = wizard_carrier_id.create({
                        "carrier_id": carrier_id.id,
                        "order_id": record.id,
                        "delivery_price": value.get("amount"),
                        "mode_freight": value.get("mode_freight").lower()
                    })
                    wizard_carrier_id.button_confirm()
                elif "order_state" in key:
                    order_state = value[key]
                elif "picking_ids" in key:
                    warehouse_updates = value
                elif "order_line" in key:
                    product_items_count = len(value.get("product_id"))

                    for i in range(0, product_items_count):
                        key_vals = {}
                        for dict_key in value.keys():
                            key_vals[dict_key] = value[dict_key][i]
                        product_items.append(key_vals)

                    updates[key] = [(0, 0, list_val) for list_val in product_items]
                else:
                    updates[key] = [(0, 0, value)]

            record.write(updates)

            if order_state not in ["po"]:
                record.action_confirm()

                if record.picking_ids.exists():
                    if warehouse_updates:
                        record.picking_ids.write(warehouse_updates)
                    if order_state and order_state in ["process"]:
                        record.action_remove_delivery_block()
                        wh_op_id = record.picking_ids.filtered_domain([
                            ("state", "in", ["confirmed", "assigned"]),
                            ('backorder_id', "=", False)
                        ])[0]
                        for move_id in wh_op_id.move_ids:
                            move_id.write({"quantity": move_id.product_uom_qty})
                        wh_op_id.button_validate()
                    elif order_state and order_state in ["ship"]:
                        wh_op_ids = record.picking_ids.filtered_domain([
                            ("state", "not in", ["done"]),
                            ('backorder_id', "=", False)
                        ])
                        for wh_id in wh_op_ids:
                            check_ids = wh_id.check_ids
                            if check_ids.exists():
                                for check in check_ids:
                                    check.write({"additional_note": "QC Passed via data upload."})
                                    check.do_pass()
                            else:
                                for move_id in wh_id.move_ids:
                                    move_id.write({"quantity": move_id.product_uom_qty})
                            wh_id.button_validate()

            if record.state in ['sale'] and record.order_line.exists():
                record.create_invoice_register_payment()

        return recordsets


class SaleOrderImportationHeader(models.TransientModel):
    _name = "sale.order.importation.header"
    _description = "Sale Order Importation Header"

    name = fields.Char()
    technical_name = fields.Char()
    importation_id = fields.Many2one('sale.order.importation')
    sequence = fields.Integer()
    is_required = fields.Boolean()
