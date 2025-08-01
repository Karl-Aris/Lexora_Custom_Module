from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_fee_if_needed(self):
        """Add 3.5% Authorize.net fee if not already added."""
        fee_product = self.env['product.product'].sudo().search([
            ('default_code', '=', 'AUTH_NET_FEE')
        ], limit=1)

        if not fee_product:
            return  # Ensure product exists

        for order in self:
            tx = self.env['payment.transaction'].sudo().search([
                ('sale_order_ids', 'in', order.id),
                ('state', '=', 'authorized'),
            ], order="id desc", limit=1)

            if not tx or tx.provider_id.code != 'authorize':
                continue

            # Check if fee already exists
            fee_line = order.order_line.filtered(lambda l: l.product_id == fee_product)
            fee_amount = round(order.amount_untaxed * 0.035, 2)

            if fee_line:
                fee_line.write({'price_unit': fee_amount})
            else:
                self.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': fee_amount,
                    'order_partner_id': order.partner_id.id,
                    'product_uom': fee_product.uom_id.id,
                })
