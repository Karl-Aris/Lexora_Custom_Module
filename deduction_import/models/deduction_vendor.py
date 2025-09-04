from odoo import models, fields, api

class DeductionVendor(models.Model):
    _name = "deduction.vendor"
    _description = "Deduction Vendor"
    _order = "deduction_date desc, id desc"

    name = fields.Char(string="Deduction #", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    sale_order_line_id = fields.Many2one("sale.order.line", string="SKU")
    sale_order_line_ids = fields.One2many("deduction.vendor.line", "deduction_id", string="Sales Order Lines")
    po_line_ids = fields.One2many("deduction.vendor.line", "deduction_id", string="PO Lines")
    product_template_id = fields.Many2one("product.template", string="Product Template")
    purchase_order = fields.Char(string="PO #", help="Purchase Order number")
    external_sku = fields.Char(string="External SKU")

    deduction_date = fields.Date(string="Deduction Date")
    deduction_total_amount = fields.Monetary(string="Deduction Total Amount", currency_field='currency_id')
    paid_amount = fields.Monetary(string="Paid Amount", currency_field='currency_id')
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id.id)

    backorder = fields.Boolean(string="Backorder")
    cogs = fields.Float(string="COGS")

    CONDITION_SELECTION = [
        ("new", "New"),
        ("used", "Used"),
        ("refurbished", "Refurbished")
    ]
    condition = fields.Selection(CONDITION_SELECTION, string="Condition")

    reason = fields.Text(string="Reason")
    resolution = fields.Text(string="Resolution")
    taken_actions = fields.Text(string="Taken Actions")

    TICKET_STATUS = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    ]
    ticket_status = fields.Selection(TICKET_STATUS, string="Ticket Status", default="open")

    # Standard Odoo fields (kept as readonly)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)
    create_date = fields.Datetime(string="Created on", readonly=True)
    create_uid = fields.Many2one("res.users", string="Created by", readonly=True)
    write_date = fields.Datetime(string="Last Updated on", readonly=True)
    write_uid = fields.Many2one("res.users", string="Last Updated by", readonly=True)

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.partner_id:
                rec.display_name = f"{rec.name} / {rec.partner_id.name}"
            else:
                rec.display_name = rec.name
