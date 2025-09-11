from odoo import models, fields, api

class ReturnOrder(models.Model):
    _name = 'return.order'
    _description = 'Return Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="PO #", required=True, tracking=True)
    return_date = fields.Date(string="Return Date", tracking=True)
    qc_condition = fields.Selection([
        ('good', 'Good'),
        ('damage', 'Damage'),
    ], string="QC Status/Condition", tracking=True)
    qc_sku = fields.Char(string="QC Status/SKU")
    carrier = fields.Char(string="Carrier")
    archive_link = fields.Char(string="Archive Link")
    notes = fields.Text(string="Notes")
    merchant = fields.Char(string="Merchant")
    date_shipped = fields.Datetime(string="Date Shipped")

    sale_order_id = fields.Many2one('sale.order', string="Sales Order", ondelete="cascade")
    picking_id = fields.Many2one('stock.picking', string="Return Picking", ondelete='set null')
    picking_name = fields.Char(related="picking_id.name", string="Picking Reference", store=True)
    state = fields.Selection([
        ('initiated', 'Return Initiated'),
        ('returned', 'Returned'),
    ], string="Status", default="initiated", tracking=True)
