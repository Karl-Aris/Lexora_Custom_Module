from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _finalize_sale_order(self, **kwargs):
        for tx in self:
            if tx.provider_code == 'authorize_net' and tx.sale_order_ids:
                for order in tx.sale_order_ids:
                    order.add_authorize_net_fee()
        return super()._finalize_sale_order(**kwargs)
