# controllers/main.py
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class LexoraShipping(http.Controller):

    @http.route(['/shop/shipping-details/confirm'], type='http', auth='public', website=True, csrf=True)
    def shipping_details_confirm(self, **post):
        purchase_order = post.get('purchase_order')
        order_customer = post.get('order_customer')
        order_phone = post.get('order_phone')
        order_address = post.get('order_address')

        # Get current order
        sale_order = request.website.sale_get_order()

        # Check if PO number already exists in another sale.order
        existing = request.env['sale.order'].sudo().search([
            ('purchase_order', '=', purchase_order),
            ('id', '!=', sale_order.id)
        ], limit=1)

        if existing:
            error = {'purchase_order': 'PO number already used. Please enter a unique value.'}
            values = {
                'error': error,
                'purchase_order': purchase_order,
                'order_customer': order_customer,
                'order_phone': order_phone,
                'order_address': order_address,
            }
            return request.render('website_sale_lexora_shipping.shipping-details', values)

        # Save the shipping info to the current sale order
        sale_order.sudo().write({
            'purchase_order': purchase_order,
            'partner_name': order_customer,
            'partner_phone': order_phone,
            'partner_street': order_address,
        })

        # Redirect to payment or next step
        return redirect('/shop/payment')
