from odoo import http
from odoo.http import request
from odoo.tools.float_utils import float_round

class PaymentFeeController(http.Controller):

    @http.route(['/payment/pay'], type='http', auth="public", website=True, csrf=False)
    def custom_payment_fee_handler(self, **post):
        order_id = post.get('order_id')
        access_token = post.get('access_token')
        acquirer_id = int(post.get('acquirer_id', 0))

        if not order_id or not acquirer_id:
            return request.redirect('/shop/checkout')

        order = request.env['sale.order'].sudo().browse(int(order_id))
        acquirer = request.env['payment.acquirer'].sudo().browse(acquirer_id)

        # Validate access token if present
        if access_token and access_token != order.access_token:
            return request.redirect('/shop/checkout')

        if acquirer.provider == 'authorize_net':
            fee_product = request.env['product.product'].sudo().search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if fee_product:
                already_has_fee = order.order_line.filtered(lambda l: l.product_id.id == fee_product.id)
                if not already_has_fee:
                    fee = float_round(order.amount_untaxed * 0.035, 2)

                    order.write({
                        'order_line': [(0, 0, {
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                            'product_uom': fee_product.uom_id.id,
                        })]
                    })

        return request.redirect(f"/payment/process?acquirer_id={acquirer_id}&order_id={order.id}&access_token={access_token}")
