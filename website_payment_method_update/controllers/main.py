from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(name)

class WebsitePaymentMethod(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth='public', website=True, csrf=True)
    def update_payment_method(self, order_id=None, x_payment_method=None, **kwargs):
        try:
            _logger.info(f"Update payment method called with order_id={order_id}, x_payment_method={x_payment_method}")
    
            if not order_id:
                _logger.error("Missing order_id in request")
                return request.redirect("/shop/checkout")
    
            if not x_payment_method:
                _logger.error("Missing x_payment_method in request")
                return request.redirect("/shop/checkout")
    
            order_id_int = int(order_id)
            order = request.env['sale.order'].sudo().browse(order_id_int)
    
            if not order.exists():
                _logger.error(f"Sale order with id {order_id} does not exist")
                return request.redirect("/shop/checkout")
    
            order.write({'x_payment_method': x_payment_method})
            _logger.info(f"Payment method updated on order {order_id}")
    
        except Exception as e:
            _logger.exception(f"Error updating payment method: {e}")
    
        return request.redirect("/shop/checkout")
