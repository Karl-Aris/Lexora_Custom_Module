from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _handle_authorize_net_fee_post_payment(self):
        for tx in self:
            if tx.provider_code != 'authorize_net':
                continue

            sale_order = tx.sale_order_ids and tx.sale_order_ids[0]
            if not sale_order or sale_order.state != 'draft':
                continue

            # Apply fee and confirm the order
            sale_order.apply_authorize_net_fee()
            sale_order.action_confirm()

    def _send_payment_request(self):
        response = super()._send_payment_request()

        # After successful payment, inject surcharge and confirm order
        if self.state == 'done':
            self._handle_authorize_net_fee_post_payment()

        return response
