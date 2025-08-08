from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_net_fee(self):
        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Remove existing surcharge lines
            surcharge_lines = order.order_line.filtered(lambda l: l.product_id == fee_product)
            surcharge_lines.unlink()

            fee_amount = round(order.amount_untaxed * 0.035, 2)
            if fee_amount > 0:
                order.order_line.create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'price_unit': fee_amount,
                    'product_uom_qty': 1,
                })

    def action_confirm(self):
        # Add surcharge line if payment method is Authorize.Net
        for order in self:
            # Detect if Authorize.Net is selected on the order:
            # This depends on your payment selection logic - adjust accordingly.
            if order.payment_method_code == 'authorize':  # example field, replace as needed
                order._add_authorize_net_fee()
        return super().action_confirm()
