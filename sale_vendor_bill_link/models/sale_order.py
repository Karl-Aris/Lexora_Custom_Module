from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'sale_order_id',
        string='Linked Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )