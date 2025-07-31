# payment_mock_authorize_net_fee/models/payment_provider.py
from odoo import models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _get_compatible_providers(self):
        return super()._get_compatible_providers() + ['mock_authorize_net']

    def _get_providers(self):
        providers = super()._get_providers()
        providers.append(('mock_authorize_net', 'Mock Authorize.Net'))
        return providers
