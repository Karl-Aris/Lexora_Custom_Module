from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _set_done(self):
        res = super()._set_done()

        for tx in self:
            provider = tx.provider_id
            if provider and provider.code == 'authorize_net' and tx.sale_order_ids:
                fee_product = self.env['product.product'].sudo().search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)

                if fee_product:
                    fee_percent = provider.authnet_fee_percent or 0.0

                    for order in tx.sale_order_ids:
                        # Remove existing fee lines to avoid duplicates
                        order.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

                        if fee_percent > 0:
                            base_amount = sum(line.price_total for line in order.order_line)
                            fee_amount = base_amount * (fee_percent / 100.0)

                            order.order_line.create({
                                'order_id': order.id,
                                'product_id': fee_product.id,
                                'name': fee_product.name,
                                'product_uom_qty': 1,
                                'price_unit': fee_amount,
                            })
        return res
