from odoo import http
from odoo.http import request

class WebsitePaymentMethod(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth='public', website=True, csrf=True)
    def update_payment_method(self, order_id=None, x_payment_method=None, **kwargs):
        try:
            if not order_id or not x_payment_method:
                return request.redirect("/shop/checkout")

            order = request.env['sale.order'].sudo().browse(int(order_id))

            if not order.exists():
                return request.redirect("/shop/checkout")

            order.write({'x_payment_method': x_payment_method})

        except Exception:
            # Swallow exceptions silently and redirect
            pass

        return request.redirect("/shop/checkout")
