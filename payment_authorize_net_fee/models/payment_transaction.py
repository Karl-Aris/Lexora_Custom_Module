from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)
        for tx in transactions:
            if tx.provider_id.code == 'authorize' and tx.sale_order_ids:
                # Add surcharge line to sale orders if missing (fallback)
                tx.sale_order_ids._add_authorize_net_fee()
                # Recompute transaction amount to match SO total including surcharge
                tx.amount = sum(so.amount_total for so in tx.sale_order_ids)
        return transactions
