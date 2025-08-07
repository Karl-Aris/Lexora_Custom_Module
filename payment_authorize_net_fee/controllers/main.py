# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class PaymentAuthorizeNetFeeController(http.Controller):
    @http.route(['/payment/authorize_net_fee'], type='http', auth='public', website=True)
    def payment_authorize_net_fee(self, order_id=None, **post):
        """Adds Authorize.Net surcharge line to the sale order and redirects to payment page."""

        if not order_id:
            return request.not_found()

        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        if not sale_order or not sale_order.exists():
            return request.not_found()

        # Make sure Authorize.Net was selected (check your exact provider code)
        selected_payment_provider = post.get('payment_provider')
        if selected_payment_provider != 'authorize':
            return request.redirect('/my/orders/%s?access_token=%s' % (
                sale_order.id, sale_order.access_token,
            ))

        # Avoid adding the fee multiple times
        existing_fee_line = sale_order.order_line.filtered(
            lambda l: l.product_id and l.product_id.default_code == 'AUTH_NET_FEE'
        )
        if not existing_fee_line:
            fee_product = request.env['product.product'].sudo().search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if not fee_product:
                return request.render('website.404')  # Show 404 if fee product missing

            surcharge_amount = sale_order.amount_untaxed * 0.035  # 3.5%
            sale_order.write({
                'order_line': [(0, 0, {
                    'product_id': fee_product.id,
                    'name': 'Authorize.Net Admin Fee',
                    'product_uom_qty': 1,
                    'price_unit': surcharge_amount,
                })]
            })

        # ✅ Redirect to payment page, not order summary — this prevents premature success message
        return request.redirect('/payment/pay?reference=%s&access_token=%s' % (
            sale_order.name, sale_order.access_token,
        ))
