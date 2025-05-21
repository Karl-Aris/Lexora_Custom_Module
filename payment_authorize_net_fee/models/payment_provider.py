
from odoo import models

class PaymentProviderAuthorizeNet(models.Model):
    _inherit = 'payment.provider'

    def _authorize_net_prepare_transaction_request_payload(self, acquirer_reference, transaction):
        payload = super()._authorize_net_prepare_transaction_request_payload(acquirer_reference, transaction)

        if self.code == 'authorize_net':
            base_amount = float(transaction.amount)
            fee = round(base_amount * 0.03, 2)
            total_with_fee = base_amount + fee

            payload['transactionRequest']['amount'] = total_with_fee

        return payload
