
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def add_authorize_net_surcharge(self):
        product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not product:
            return

        for order in self:
            # Remove any previous surcharge lines
            order.order_line.filtered(lambda l: l.product_id == product).unlink()

            if hasattr(order, 'payment_provider_id') and order.payment_provider_id.code == 'authorize_net':
                fee_amount = round(order.amount_total * 0.03, 2)
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'name': 'Authorize.Net Surcharge (3%)',
                    'product_uom_qty': 1,
                    'price_unit': fee_amount,
                })
