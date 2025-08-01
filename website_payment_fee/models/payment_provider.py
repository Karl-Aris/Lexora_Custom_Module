from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    fixed_fee = fields.Monetary("Fixed Fee", currency_field='currency_id')
    percentage_fee = fields.Float("Percentage Fee (%)")