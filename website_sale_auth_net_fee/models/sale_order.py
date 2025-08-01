from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _add_authorize_fee(self):
        fee_product = self.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            if order.payment_acquirer_id.provider != 'authorize':
                continue

            existing_fee_line = order.order_line.filtered(lambda l: l.product_id == fee_product)
            fee = order.amount_untaxed * 0.035

            if existing_fee_line:
                existing_fee_line.write({'price_unit': round(fee, 2)})
            else:
                self.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': round(fee, 2),
                    'order_partner_id': order.partner_id.id,
                })

    def action_confirm(self):
        self._add_authorize_fee()
        return super().action_confirm()
