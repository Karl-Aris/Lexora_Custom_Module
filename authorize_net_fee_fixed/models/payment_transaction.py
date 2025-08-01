from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _set_transaction_done(self):
        res = super()._set_transaction_done()
        for tx in self:
            if tx.sale_order_ids:
                for order in tx.sale_order_ids:
                    # Set payment provider
                    order.payment_provider_id = tx.provider_id

                    if tx.provider_id.code == 'authorize':
                        fee_product = tx.env['product.product'].sudo().search([
                            ('default_code', '=', 'AUTH_NET_FEE')
                        ], limit=1)

                        if fee_product and not order.order_line.filtered(lambda l: l.product_id == fee_product):
                            fee = round(order.amount_untaxed * 0.035, 2)
                            tx.env['sale.order.line'].sudo().create({
                                'order_id': order.id,
                                'product_id': fee_product.id,
                                'name': fee_product.name,
                                'product_uom_qty': 1,
                                'price_unit': fee,
                                'order_partner_id': order.partner_id.id,
                                'product_uom': fee_product.uom_id.id,
                            })
        return res
