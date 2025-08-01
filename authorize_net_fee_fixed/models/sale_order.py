from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_provider_id = fields.Many2one(
        'payment.provider', string="Payment Provider", readonly=False
    )
