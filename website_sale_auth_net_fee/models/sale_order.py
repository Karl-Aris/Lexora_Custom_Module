from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_acquirer_id = fields.Many2one(
        'payment.acquirer',
        string="Payment Acquirer",
        help="The payment method selected by the customer during checkout."
    )

    def _add_authorize_fee(self):
        fee_product = self.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Skip if no payment method set or not authorize.net
            if not order.payment_acquirer_id or order.payment_acquirer_id.provider != 'authorize':
                continue

            # Check if fee already added
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

    def action_confirm(self):
        self._add_authorize_fee()
        return super().action_confirm()
