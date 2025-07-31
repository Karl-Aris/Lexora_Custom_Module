from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mock_authorize_net', "Mock Authorize.Net")]
    )
