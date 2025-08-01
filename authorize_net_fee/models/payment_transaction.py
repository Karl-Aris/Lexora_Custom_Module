from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _reconcile_after_done(self):
        res = super()._reconcile_after_done()
        for tx in self:
            if tx.acquirer_id.provider == 'authorize' and tx.sale_order_ids:
                for order in tx.sale_order_ids:
                    order._add_authorize_fee()
        return res
