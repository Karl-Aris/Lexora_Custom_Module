from odoo import models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _get_providers(self):
        providers = super()._get_providers()
        providers.append(('mock_authorize_net', 'Mock Authorize.Net'))
        return providers
