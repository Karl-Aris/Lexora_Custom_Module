from odoo import http
from odoo.http import request

class WebsitePaymentMethod(http.Controller):

    @http.route(['/shop/payment_method/update'], type='http', auth='user', website=True, csrf=True)
    def update_payment_method(self, order_id=None, x_payment_method=None, **kwargs):
        """
        Custom route to update the custom payment method field on the sale.order.
        """
        order = request.website.sale_get_order()
    
        # Basic checks
        if not order or not x_payment_method:
            return request.redirect("/shop/shipping-details")
    
        # Write custom field
        try:
            order.sudo().write({'x_payment_method': x_payment_method})
        except Exception:
            pass  # Optionally log error here
    
        return request.redirect("/shop/shipping-details")

