from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(name)

class WebsitePaymentMethod(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth='public', website=True, csrf=True)
    def update_payment_method(self, order_id=None, x_payment_method=None, **kwargs):
        _logger.info(f"Update payment method called with order_id={order_id}, x_payment_method={x_payment_method}")
        if order_id and x_payment_method:
            order = request.env['sale.order'].sudo().browse(int(order_id))
            if order.exists():
                order.write({'x_payment_method': x_payment_method})
                _logger.info(f"Payment method updated on order {order_id}")
            else:
                _logger.warning(f"Order {order_id} not found")
        else:
            _logger.warning("Missing order_id or x_payment_method")
        return request.redirect("/shop/checkout")
