from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    fee_percent = fields.Float(string="Fee Percentage", default=0.0)