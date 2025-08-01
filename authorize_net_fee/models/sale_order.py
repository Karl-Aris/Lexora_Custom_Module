from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _add_authorize_fee(self):
        fee_product = self.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Don't add again if already added
            existing_fee_line = order.order_line.filtered(lambda l: l.product_id == fee_product)
            fee = round(order.amount_untaxed * 0.035, 2)

            if existing_fee_line:
                existing_fee_line.write({'price_unit': fee})
            else:
                self.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': fee,
                    'order_partner_id': order.partner_id.id,
                    'product_uom': fee_product.uom_id.id,
                })
