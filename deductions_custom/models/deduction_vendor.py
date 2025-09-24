from odoo import models, fields, api

class DeductionVendor(models.Model):
    _name = 'deduction.vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Deductions'
    _order = 'deduction_date desc'
    
    message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: [('model', '=', self._name)],
        string='Messages',
        readonly=True
    )

    name = fields.Char(string="Deduction #", required=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain="[('name', 'in', ['Lowe\'s', 'Wayfair', 'Home Depot', 'Amazon', 'Overstock'])]",
        tracking=True
    )
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', readonly=True)

    purchase_order = fields.Char(string='Search PO #', tracking=True)
    sku = fields.Char(string='SKU')
    external_sku = fields.Char(string='External SKU')

    deduction_date = fields.Date(string='Deduction Date', default=fields.Date.context_today, tracking=True)
    deduction_total_amount = fields.Monetary(string='Deduction Total Amount')
    paid_amount = fields.Monetary(string='Paid Amount (Sales)', readonly=True)
    sku_paid_amount = fields.Monetary(string='Paid Amount (SKU)')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    cogs = fields.Float(string='COGS')

    ticket_status = fields.Selection([
        ('filed_creative', 'FILED - CREATIVE'),
        ('filed_damaged', 'FILED - DAMAGED'),
        ('filed_damage', 'FILED - DAMAGE'),
        ('filed_out_of_policy', 'FILED - OUTOFPOLICY'),
        ('filed_duplicate', 'FILED - DUPLICATE'),
        ('filed_missing_item', 'FILED - MISSING ITEM'),
        ('filed_missing_product', 'FILED - MISSING PRODUCT'),
        ('filed_modified', 'FILED - MODIFIED'),
        ('filed_not_our_product', 'FILED - NOT OUR PRODUCT'),
        ('filed_not_shipped', 'FILED - NOT SHIPPED'),
        ('filed_pod', 'FILED - POD'),
        ('filed_fake', 'FILED - FAKE'),
        ('in_progress', 'IN PROGRESS'),
        ('missing_parts', 'MISSING PARTS'),
        ('lost', 'LOST'),
        ('damaged', 'DAMAGED'),
        ('lost_fc', 'LOST FC'),
        ('not_filed', 'NOT FILED'),
        ('not_shipped', 'NOT SHIPPED'),
        ('open', 'OPEN'),
        ('partially_refunded', 'PARTIALLY REFUNDED'),
        ('partially_won', 'PARTIALLY WON'),
        ('por', 'POR'),
        ('refiled', 'REFILED'),
        ('resolved', 'RESOLVED'),
        ('closed', 'CLOSED'),
        ('won', 'WON'),
    ], string='Ticket Status', default='open')

    reason = fields.Text(string='Reason')
    resolution = fields.Text(string='Resolution')
    taken_actions = fields.Text(string='Taken Actions')

    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        compute='_compute_sale_order_lines',
        string='Sales Order Lines'
    )

    sku_info = fields.One2many(
        'deduction.vendor.line',
        'deduction_id',
        string="SKU Info"
    )
    
    po_numbers_from_lines = fields.Char(
        string="PO # (from SKU Info)",
        compute='_compute_po_numbers_from_lines',
        store=False
    )
    
    deduction_total_amount_view = fields.Monetary(
        string='Deduction Total (from SKU)',
        compute='_compute_deduction_total_amount_view',
        store=True,
        currency_field='currency_id'
    )
    
    def _auto_assign_all_lines_by_name(self):
        for record in self:
            if not record.name:
                continue
            matching_lines = self.env['deduction.vendor.line'].search([
                ('deduction_id.name', '=', record.name),
                ('deduction_id', '=', record.id)
            ])
            matching_lines.write({'deduction_id': record.id})

    @api.depends('sku_info.deduction_total_amount')
    def _compute_deduction_total_amount_view(self):
        for rec in self:
            rec.deduction_total_amount_view = sum(
                line.deduction_total_amount or 0.0 for line in rec.sku_info
            )

    @api.depends('sku_info.purchase_order')
    def _compute_po_numbers_from_lines(self):
        for rec in self:
            po_set = {line.purchase_order for line in rec.sku_info if line.purchase_order}
            rec.po_numbers_from_lines = ', '.join(sorted(po_set))

    @api.depends('sale_order_id')
    def _compute_sale_order_lines(self):
        for record in self:
            if record.sale_order_id:
                record.sale_order_line_ids = record.sale_order_id.order_line
            else:
                record.sale_order_line_ids = False

    @api.onchange('purchase_order')
    def _onchange_purchase_order(self):
        if self.purchase_order:
            sale_order = self.env['sale.order'].search([('purchase_order', '=', self.purchase_order)], limit=1)
            if sale_order:
                self.sale_order_id = sale_order
                self.partner_id = sale_order.partner_id
                self.paid_amount = sale_order.amount_total
                self.currency_id = sale_order.currency_id

                # Populate SKU Info lines
                lines = []
                for line in sale_order.order_line:
                    lines.append((0, 0, {
                        'purchase_order': self.purchase_order,
                        'sale_order_id': sale_order.id,
                        'sku_id': line.product_id.id,
                        'external_sku': '',  # Optional if not in order_line
                        'deduction_total_amount': 0.0,
                        'sku_paid_amount': 0.0,
                        'cogs': line.product_id.standard_price,
                        'ticket_status': 'open',
                        'currency_id': sale_order.currency_id.id,
                    }))
                self.sku_info = lines
            else:
                self.sale_order_id = False
                self.sku_info = [(5, 0, 0)]  # Clear sku_info

    @api.model
    def create(self, vals):
        # ✅ Auto-generate 'name' using a sequence if not provided
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('deduction.vendor') or '/'

        # ✅ Automatically link to sale order if PO is matched
        if 'purchase_order' in vals and not vals.get('sale_order_id'):
            sale_order = self.env['sale.order'].search([('purchase_order', '=', vals['purchase_order'])], limit=1)
            if sale_order:
                vals['sale_order_id'] = sale_order.id
                vals['partner_id'] = sale_order.partner_id.id
                vals['paid_amount'] = sale_order.amount_total
                vals['currency_id'] = sale_order.currency_id.id  # Set currency too, if needed

        # ✅ Create the deduction record first
        record = super(DeductionVendor, self).create(vals)

        # ✅ Populate sku_info lines from sale order lines if sale_order_id is set
        if record.sale_order_id:
            lines = []
            for sol in record.sale_order_id.order_line:
                lines.append((0, 0, {
                    'deduction_id': record.id,
                    'purchase_order': record.purchase_order or '',
                    'sale_order_id': record.sale_order_id.id,
                    'sku_id': sol.product_id.id,
                    'external_sku': '',  # Optional
                    'deduction_total_amount': 0.0,
                    'sku_paid_amount': 0.0,
                    'cogs': sol.product_id.standard_price or 0.0,
                    'ticket_status': 'open',
                    'currency_id': record.currency_id.id,
                }))
            record.sku_info = lines

        # ✅ Post a welcome message in chatter for new record
        record.message_post(
            body="Welcome! This is a new deduction record. Start adding your notes and communications here."
        )

        return record

    
    sku_info_grouped = fields.One2many(
        'deduction.vendor.line',
        compute='_compute_sku_info_grouped',
        string='All SKU Info (Grouped by Deduction #)',
    )

    @api.depends('name')
    def _compute_sku_info_grouped(self):
        for record in self:
            if not record.name:
                record.sku_info_grouped = [(5, 0, 0)]
                continue
            matching_lines = self.env['deduction.vendor.line'].search([
                ('deduction_id.name', '=', record.name)
            ])
            record.sku_info_grouped = matching_lines
            
    missing_po_list = fields.Text(
        string="Non-existing PO#",
        compute='_compute_missing_pos',
        store=False
    )
    
    @api.depends('sku_info.purchase_order')
    def _compute_missing_pos(self):
        for record in self:
            missing = []
            existing_pos = self.env['sale.order'].search([]).mapped('purchase_order')
            for line in record.sku_info:
                if line.purchase_order and line.purchase_order not in existing_pos:
                    missing.append(line.purchase_order)
            record.missing_po_list = ', '.join(sorted(set(missing)))
            
    
class DeductionVendorLine(models.Model):
    _name = 'deduction.vendor.line'
    _description = 'Deductions Line'
    
    purchase_order = fields.Char(string='PO #')

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        compute='_compute_sale_order_id',
        store=True,
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        compute='_compute_partner_id',
        store=True,
    )
    
    invoice_status = fields.Selection(
        related='sale_order_id.invoice_status',
        string='Invoice Status',
        store=True,
        readonly=True
    )

    condition = fields.Selection([
        ('good', 'GOOD'),
        ('damaged', 'DAMAGED'),
        ('none', 'To Do')
    ], string='Condition', compute='_compute_quality_fields', store=True)

    quality_state = fields.Selection([
        ('none', 'To Do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')
    ], string='Quality Status', compute='_compute_quality_fields', store=True)

    picking_id = fields.Many2one('stock.picking', string="Picking", compute='_compute_quality_fields', store=True)
    
    x_location_display = fields.Text(
        string="Return Location",
        compute='_compute_quality_fields',
        store=False,
        readonly=True
    )
    
    @api.depends('purchase_order')
    def _compute_partner_id(self):
        for line in self:
            if line.purchase_order:
                sale_order = self.env['sale.order'].search([('purchase_order', '=', line.purchase_order)], limit=1)
                line.partner_id = sale_order.partner_id.id if sale_order else False
            else:
                line.partner_id = False
    
    @api.depends('sale_order_id', 'sku_id')
    def _compute_quality_state(self):
        for line in self:
            line.quality_state = 'none'  # default

            if not line.sale_order_id or not line.sku_id:
                continue

            qc = self.env['quality.check'].search([
                ('x_studio_sale_order', '=', line.sale_order_id.id),
                ('product_id', '=', line.sku_id.id)
            ], limit=1)

            if qc:
                line.quality_state = qc.quality_state or 'none'

    @api.depends('sale_order_id', 'sku_id')
    def _compute_quality_fields(self):
        for line in self:
            # Defaults
            line.quality_state = 'none'
            line.picking_id = False
            line.x_location_display = ''
            line.condition = ''

            if not line.sale_order_id or not line.sku_id or not line.sku_id.default_code:
                continue

            # Search for quality check using SKU (default_code) and SO
            qc = self.env['quality.check'].search([
                ('x_studio_sale_order', '=', line.sale_order_id.id),
                ('product_id.default_code', '=', line.sku_id.default_code)
            ], limit=1)

            if qc:
                line.quality_state = qc.quality_state or 'none'
                line.picking_id = qc.picking_id
                line.x_location_display = qc.x_location or ''

                if qc.quality_state == 'pass':
                    line.condition = 'good'
                elif qc.quality_state == 'fail':
                    line.condition = 'damaged'
                else:
                    line.condition = 'none'  # This will show as "To Do" in selection
            else:
                # No QC found — leave condition empty (not "To Do")
                line.condition = ''

    @api.depends('picking_id', 'quality_state')
    def _compute_condition(self):
        for line in self:
            line.condition = 'none'  # default
            picking_name = (line.picking_id.name or '').upper()

            if 'RETURN' in picking_name:
                if line.quality_state == 'pass':
                    line.condition = 'good'
                elif line.quality_state == 'fail':
                    line.condition = 'damaged'
                else:
                    line.condition = 'none'


    @api.onchange('purchase_order')
    def _onchange_purchase_order(self):
        if self.purchase_order:
            sale_order = self.env['sale.order'].search([('purchase_order', '=', self.purchase_order)], limit=1)
            if sale_order:
                self.sale_order_id = sale_order.id
                self.partner_id = sale_order.partner_id.id
            else:
                self.sale_order_id = False
                self.partner_id = False
        else:
            self.sale_order_id = False
            self.partner_id = False
            
    @api.onchange('sku_id')
    def _onchange_sku_id(self):
        self.cogs = 0.0
        self.sale_order_id = False
        self.partner_id = False

        if self.sku_id and self.purchase_order:
            # Find the matching sale.order.line by PO and SKU
            line = self.env['sale.order.line'].search([
                ('order_id.purchase_order', '=', self.purchase_order),
                ('product_id', '=', self.sku_id.id)
            ], limit=1)

            if line:
                self.sale_order_id = line.order_id.id
                self.partner_id = line.order_id.partner_id.id
                self.cogs = self.sku_id.standard_price or 0.0

    
    @api.model
    def create(self, vals):
        if not vals.get('deduction_id') and self.env.context.get('default_deduction_id'):
            vals['deduction_id'] = self.env.context['default_deduction_id']

        record = super().create(vals)

        sale_order = record.sale_order_id
        if (
            sale_order
            and record.deduction_id
            and hasattr(sale_order, 'x_deduction_id')
            and not sale_order.x_deduction_id
        ):
            sale_order.write({'x_deduction_id': record.deduction_id.id})

        return record
    @api.depends('purchase_order')
    def _compute_sale_order_id(self):
        for line in self:
            sale_order = self.env['sale.order'].search([('purchase_order', '=', line.purchase_order)], limit=1)
            line.sale_order_id = sale_order.id if sale_order else False

    original_deduction_id = fields.Many2one('deduction.vendor', string="Original Deduction")
    deduction_id = fields.Many2one('deduction.vendor', string='Deduction Reference', ondelete='cascade')
    name = fields.Char(related='deduction_id.name', string="Deduction #", store=True)
    deduction_date = fields.Date(related='deduction_id.deduction_date', string='Deduction Date', store=True)
    po_number = fields.Char(string='PO Number')
    sku_id = fields.Many2one('product.product', string='SKU')
    external_sku = fields.Char(string='External SKU')
    deduction_total_amount = fields.Monetary(string='Deduction Total Amount')
    sku_paid_amount = fields.Monetary(string='Paid Amount (SKU)')
    cogs = fields.Float(string='COGS')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    reason = fields.Text(string='Reason')
    resolution = fields.Text(string='Resolution')
    taken_actions = fields.Text(string='Taken Actions')

    ticket_status = fields.Selection([
        ('filed_creative', 'FILED - CREATIVE'),
        ('filed_damaged', 'FILED - DAMAGED'),
        ('filed_damage', 'FILED - DAMAGE'),
        ('filed_out_of_policy', 'FILED - OUTOFPOLICY'),
        ('filed_duplicate', 'FILED - DUPLICATE'),
        ('filed_missing_item', 'FILED - MISSING ITEM'),
        ('filed_missing_product', 'FILED - MISSING PRODUCT'),
        ('filed_modified', 'FILED - MODIFIED'),
        ('filed_not_our_product', 'FILED - NOT OUR PRODUCT'),
        ('filed_not_shipped', 'FILED - NOT SHIPPED'),
        ('filed_pod', 'FILED - POD'),
        ('filed_fake', 'FILED - FAKE'),
        ('in_progress', 'IN PROGRESS'),
        ('missing_parts', 'MISSING PARTS'),
        ('lost', 'LOST'),
        ('damaged', 'DAMAGED'),
        ('lost_fc', 'LOST FC'),
        ('not_filed', 'NOT FILED'),
        ('not_shipped', 'NOT SHIPPED'),
        ('open', 'OPEN'),
        ('partially_refunded', 'PARTIALLY REFUNDED'),
        ('partially_won', 'PARTIALLY WON'),
        ('por', 'POR'),
        ('refiled', 'REFILED'),
        ('resolved', 'RESOLVED'),
        ('closed', 'CLOSED'),
        ('won', 'WON'),
    ], string='Ticket Status', default='open')
    
    deduction_status = fields.Selection([
        ('', ''),
        ('processed', 'Processed'),
    ], string='Status', default='')
