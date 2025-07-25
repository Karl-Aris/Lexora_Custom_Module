from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='x_sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')],
    )
