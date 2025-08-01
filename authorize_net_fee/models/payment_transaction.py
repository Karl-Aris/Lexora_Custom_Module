from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _reconcile_after_done(self):
        res = super()._reconcile_after_done()
        for tx in self:
            if tx.sale_order_ids and tx.provider_id.code == 'authorize':
                for order in tx.sale_order_ids:
                    order.payment_provider_id = tx.provider_id
                    order._add_authorize_fee()
        return res
