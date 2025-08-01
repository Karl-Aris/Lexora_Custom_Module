from odoo import models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    # Reserved for future expansion (e.g. fee percentage config)
