from odoo import http
from odoo.http import request

class WebsitePaymentMethod(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth='public', website=True, csrf=True)
    def update_payment_method(self, order_id=None, x_payment_method=None, **kwargs):
        if order_id and x_payment_method:
            order = request.env['sale.order'].sudo().browse(int(order_id))
            if order.exists():
                order.write({'x_payment_method': x_payment_method})
        return request.redirect("/shop/checkout")
