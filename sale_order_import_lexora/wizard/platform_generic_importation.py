from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
import datetime
import xlrd
import base64
from pandas.tseries.api import guess_datetime_format


class PlatformGenericImportationWizard(models.TransientModel):
    _name = "platform.generic.importation"
    _description = "Platform Generic Importation Wizard"

    attachment = fields.Binary(string="File", required=True)
    platform_id = fields.Many2one('platform.import', required=True)
    line_ids = fields.One2many('platform.generic.lines', 'platform_id', related="platform_id.line_ids")
    has_header_error = fields.Boolean(default=False)
    header_error_display = fields.Html()
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        store=True, readonly=False,
        default=lambda self: self.env.ref("sale_order_payment_term_lexora.account_payment_term_pick_then_book"))

    def _get_partner_id(self, name):
        partner_id = self.env['res.partner'].search([("name", '=ilike', name)], limit=1)
        if not partner_id.exists():
            partner_id = partner_id.create({"name": name})
        return partner_id

    def _get_product_id(self, sku, row_index=None):
        PRODUCT = self.env['product.product']
        product_id = PRODUCT.search([
            "|",
            ("default_code", "=ilike", sku),
            ("product_dealer_sku_ids.sku", "=ilike", sku),
        ], limit=1)
        if not product_id.exists() and row_index:
            raise UserError(
                "Product SKU [%s] at [row %s] not found, please check your input before importing."
                % (sku, row_index)
            )
        return product_id
    # newly customize logic on SO
    def _execute_post_actions(self, actions):
        SO = self.env['sale.order']
        for action in actions:
            po, dict_values = list(action.items())[0]

            so_id = SO.search([("purchase_order", "=ilike", po)], limit=1)
            if not so_id.exists():
                continue

            data_to_write = {"payment_term_id": self.payment_term_id.id}

            if "order_line" in dict_values:
                for line_vals in dict_values["order_line"]:
                    line_vals["order_id"] = so_id.id
                    self.env['sale.order.line'].create(line_vals)

            so_id.write(data_to_write)

    def action_upload(self):
        workbook = self._open_workbook()
        worksheet = workbook.sheet_by_index(0)

        header_sequence, has_merchant_field = self._get_header_sequence(worksheet)

        SO = self.env['sale.order']
        create_recordsets = []
        post_actions = []
        for row_index in range(1, worksheet.nrows):
            row_values = worksheet.row_values(row_index)

            create_dict = {}
            currect_action = {}
            current_po = None
            current_sku = None
            skip_po = False
            has_sku = False
            for cell in header_sequence:
                field = cell['field']
                index = cell['index']
                field_type = cell['field_type']
                field_relation = cell['field_relation']
                field_value = row_values[index]

                if field_value in ["N/A", "n/a", "N/a", "", False, None, " "]:
                    continue

                if field in ["purchase_order"]:
                    try:
                        field_value = int(field_value)
                    except ValueError:
                        field_value = str(field_value)
                    current_po = field_value

                    action_exists = list(filter(lambda po: po.get(current_po), post_actions))
                    if action_exists:
                        action_index = post_actions.index(action_exists[0])
                        currect_action = post_actions[action_index]
                        skip_po = True
                    else:
                        currect_action[current_po] = {"order_line": []}

                elif field in ["order_phone"]:
                    field_value = str(field_value).split(".")[0]

                elif field in ["partner_id"]:
                    field_value = self._get_partner_id(field_value).id

                elif field in ["order_line_sku"]:
                    current_sku = field_value
                    product_id = self._get_product_id(current_sku, row_index)
                    if product_id.exists():
                        has_sku = True
                    currect_action[current_po]['order_line'].append({
                        "product_id": product_id.id,
                        "name": product_id.name,
                    })
                    continue

                elif field in ["order_line_quantity"]:
                    currect_action[current_po]['order_line'][-1].update(product_uom_qty=field_value)
                    continue

                elif field in ["order_line_amount"]:
                    if isinstance(field_value, str):
                        field_value = float(field_value.replace("$", "").replace(",", ""))
                    currect_action[current_po]['order_line'][-1].update(price_unit=field_value)
                    continue

                elif field in ["order_line_desc"]:
                    if has_sku is False:
                        currect_action[current_po]['order_line'].append({"name": field_value, "display_type": "line_note"})
                    continue

                elif field_type in ['date', 'datetime']:
                    if not field_value:
                        continue
                    if isinstance(field_value, float):
                        field_value = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=field_value)
                    else:
                        guessed_date_format = guess_datetime_format(field_value)
                        field_value = datetime.datetime.strptime(field_value, guessed_date_format)

                if create_dict.get(field):
                    field_value = "%s, %s" % (create_dict.get(field), field_value)

                create_dict[field] = field_value

            if not has_merchant_field:
                create_dict["partner_id"] = self._get_partner_id(self.platform_id.name).id

            if not skip_po:
                post_actions.append(currect_action)
                create_recordsets.append(create_dict)

        record_ids = SO.create(create_recordsets)
        self._execute_post_actions(post_actions)
        return self._view_uploaded_records(len(create_recordsets), record_ids)

    def _view_uploaded_records(self, total, record_ids):
        action = {
            'name': _('Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'views': [
                [self.env.ref("sale.view_quotation_tree_with_onboarding").id, 'list'],
                [self.env.ref("sale.view_order_form").id, 'form'],
            ],
            'domain': [("id", "in", record_ids.ids)]
        }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Importation Complete'),
                'message': '%s of %s records successfully imported.' % (len(record_ids), total),
                'sticky': False,
                'next': action,
            },
        }

    def cancel_button(self):
        pass

    def _open_workbook(self):
        attachment = base64.b64decode(self.attachment)
        workbook = xlrd.open_workbook(file_contents=attachment)
        return workbook

    def _get_header_sequence(self, worksheet):
        sheet_headers = worksheet.row_values(0)

        header_sequence = []
        has_merchant_field = False
        for line_id in self.line_ids:
            seq = sheet_headers.index(line_id.name)

            if line_id.field_id.field_name in ["partner_id"]:
                has_merchant_field = True

            header_sequence.append({
                "index": seq,
                "field": line_id.field_id.field_name,
                "field_type": line_id.field_id.field_type,
                "field_relation": line_id.field_id.field_relation,
            })
        return header_sequence, has_merchant_field

    def _check_headers(self):
        workbook = self._open_workbook()
        worksheet = workbook.sheet_by_index(0)
        sheet_headers = worksheet.row_values(0)

        error_headers = []
        for line_id in self.line_ids:
            if line_id.name not in sheet_headers:
                error_headers.append(line_id.name)

        if error_headers:
            error_msg = """
                <div class='alert alert-danger'>
                    <p>
                        <strong>Some field/s are not exists in header:</strong>
                        <ul>%s</ul>
                    </p>
            """ % "".join(f"<li>{item}</li>" for item in error_headers)
            error_msg += """
                    <small>
                        <i>
                            <strong>Please make sure that on your XLS import file, the first row contains all the required headers.</strong>
                        </i>
                    </small>
                </div>
            """
            self.write({
                "has_header_error": True,
                "header_error_display": error_msg
            })
        else:
            self.write({
                "has_header_error": False,
                "header_error_display": ""
            })

    @api.onchange("attachment", "platform_id")
    def _onchange_attachment_platform_id(self):
        if self.attachment and self.platform_id:
            try:
                self._check_headers()
            except xlrd.XLRDError:
                raise UserError("Only supported XLS format.")
