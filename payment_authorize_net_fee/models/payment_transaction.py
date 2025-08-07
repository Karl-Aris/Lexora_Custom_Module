from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)

        for tx in transactions:
            provider = tx.provider_id
            if (
                provider.code == 'authorize'
                and tx.sale_order_ids
            ):
                fee_product = tx.env['product.product'].search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)

                if fee_product:
                    for so in tx.sale_order_ids:
                        # Remove previous surcharge lines if any
                        so.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

                        fee = round(so.amount_untaxed * 0.035, 2)
                        if fee > 0:
                            so.order_line.create({
                                'order_id': so.id,
                                'product_id': fee_product.id,
                                'name': fee_product.name,
                                'price_unit': fee,
                                'product_uom_qty': 1,
                            })
        return transactions