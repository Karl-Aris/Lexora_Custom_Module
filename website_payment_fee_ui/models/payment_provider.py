from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    payment_fee_percent = fields.Float(string='Payment Fee (%)')
    payment_fee_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Payment Fee Product',
        domain="[('sale_ok', '=', True)]"
    )
