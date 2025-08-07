
from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    authnet_fee_percent = fields.Float(string='Authorize.Net Fee (%)', default=3.5)
