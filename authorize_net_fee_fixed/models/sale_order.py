from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_acquirer_id = fields.Many2one('payment.acquirer', string="Payment Acquirer")

    def _add_authorize_fee(self):
        fee_product = self.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return

        for order in self:
            # Make sure payment_acquirer_id exists and is Authorize.net
            if order.payment_acquirer_id.provider != 'authorize':
                continue

            # Check if fee line already exists
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


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.model
    def _get_tx_from_feedback_data(self, data, acquirer=None):
        tx = super()._get_tx_from_feedback_data(data, acquirer)
        if tx and tx.sale_order_ids:
            for order in tx.sale_order_ids:
                order.payment_acquirer_id = tx.acquirer_id  # set the payment method on SO
                order._add_authorize_fee()  # inject fee if Authorize.net
        return tx
