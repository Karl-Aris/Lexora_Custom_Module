from odoo import models

class PaymentProviderMockAuthorizeNet(models.Model):
    _inherit = 'payment.provider'

    def _get_provider_selection(self):
        selection = super()._get_provider_selection()
        selection.append(('mock_authorize_net', 'Mock Authorize.Net'))
        return selection
