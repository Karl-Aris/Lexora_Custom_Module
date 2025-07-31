from odoo import models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _get_provider_selection(self):
        """Add 'mock_authorize_net' to available providers."""
        providers = super()._get_provider_selection()
        providers.append(('mock_authorize_net', 'Mock Authorize.Net'))
        return providers

    def _is_compatible_with_journal(self, code):
        """Declare the mock provider as compatible with journals."""
        if code == 'mock_authorize_net':
            return True
        return super()._is_compatible_with_journal(code)
