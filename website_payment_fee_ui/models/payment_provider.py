from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    fee_percentage = fields.Float(
        string="Fee Percentage (%)",
        help="Percentage of the order subtotal to apply as a payment processing fee."
    )
    fee_product_id = fields.Many2one(
        'product.product',
        string="Fee Product",
        domain=[('type', '=', 'service')],
        help="Product used to record the payment provider fee on the sale order."
    )
