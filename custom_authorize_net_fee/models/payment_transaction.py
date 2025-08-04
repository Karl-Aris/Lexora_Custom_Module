from odoo import models, api, SUPERUSER_ID

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _handle_authorize_net_fee_post_payment(self):
        for tx in self:
            if tx.provider_code != 'authorize_net':
                continue

            sale_order = tx.sale_order_ids and tx.sale_order_ids[0]
            if not sale_order or sale_order.state not in ['draft', 'sent']:
                continue

            env = api.Environment(self.env.cr, SUPERUSER_ID, {})
            sale_order_sudo = env['sale.order'].browse(sale_order.id)

            if not sale_order_sudo.authorize_fee_applied:
                sale_order_sudo.apply_authorize_net_fee()
            sale_order_sudo.action_confirm()

    def _execute_callback(self):
        res = super()._execute_callback()
        if self.state == 'done':
            self._handle_authorize_net_fee_post_payment()
        return res
