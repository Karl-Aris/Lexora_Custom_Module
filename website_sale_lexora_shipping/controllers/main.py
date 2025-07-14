# controllers/main.py

from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class LexoraShipping(http.Controller):

    @http.route(['/shop/shipping-details/confirm'], type='http', auth='user', website=True, csrf=True)
    def shipping_details_confirm(self, **post):
        purchase_order = post.get('purchase_order', '').strip()
        order_customer = post.get('order_customer', '').strip()
        order_phone = post.get('order_phone', '').strip()
        order_address = post.get('order_address', '').strip()

        sale_order = request.website.sale_get_order()

        if not sale_order:
            return request.redirect('/shop')

        # Check for duplicate PO #
        existing = request.env['sale.order'].sudo().search([
            ('purchase_order', '=', purchase_order),
            ('id', '!=', sale_order.id)
        ], limit=1)

        if existing:
            values = {
                'error': {'purchase_order': 'PO number already used. Please enter a unique value.'},
                'purchase_order': purchase_order,
                'order_customer': order_customer,
                'order_phone': order_phone,
                'order_address': order_address,
            }
            return request.render('website_sale_lexora.shipping-details', values)

        # Update the sale.order
        sale_order.sudo().write({
            'purchase_order': purchase_order,
            'partner_name': order_customer,
            'partner_phone': order_phone,
            'partner_street': order_address,
        })

        return redirect('/shop/payment')
