from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_net_fee(self):
        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Remove previous surcharge lines if any
            order.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

            fee = round(order.amount_untaxed * 0.035, 2)
            if fee > 0:
                order.order_line.create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'price_unit': fee,
                    'product_uom_qty': 1,
                })
