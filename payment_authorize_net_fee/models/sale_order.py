from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_net_fee(self):
        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            order.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

            provider = self.env.context.get('payment_provider_code')
            if provider == 'authorize_net':
                fee_percent = self.env['payment.provider'].sudo().search([
                    ('code', '=', 'authorize_net')
                ], limit=1).authnet_fee_percent or 0.0

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
