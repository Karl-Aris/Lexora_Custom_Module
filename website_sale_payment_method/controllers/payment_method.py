from odoo import http
from odoo.http import request

class PaymentMethodController(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth="public", methods=['POST'], csrf=True, website=True)
    def update_payment_method(self, **post):
        order_id = post.get('order_id')
        payment_method = post.get('x_payment_method')

        if not order_id or not payment_method:
            return request.redirect('/shop/checkout')

        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        if sale_order.exists():
            sale_order.write({'x_payment_method': payment_method})

        return request.redirect('/shop/checkout')
