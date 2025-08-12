from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_net_fee(self):
        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Remove existing surcharge and note lines
            surcharge_lines = order.order_line.filtered(lambda l: l.product_id == fee_product)
            note_lines = order.order_line.filtered(lambda l: l.display_type == 'line_note' and 'Authorize.Net' in (l.name or ''))
            (surcharge_lines | note_lines).unlink()

            # Calculate fee
            fee_amount = round(order.amount_untaxed * 0.035, 2)
            if fee_amount > 0:
                # Add surcharge product line
                fee_line = self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'price_unit': fee_amount,
                    'product_uom_qty': 1,
                })

                # Add note line right after surcharge
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'name': 'A 3.5% Authorize.Net payment processing fee has been applied to your order.',
                    'display_type': 'line_note',
                    'sequence': fee_line.sequence + 1,  # place directly after fee
                })

    def action_confirm(self):
        for order in self:
            if order.x_payment_method == 'authorize':
                order._add_authorize_net_fee()
        return super().action_confirm()
