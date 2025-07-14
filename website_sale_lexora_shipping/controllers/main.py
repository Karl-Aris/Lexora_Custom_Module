# controllers/main.py
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class LexoraShipping(http.Controller):

    @http.route(['/shop/shipping-details/confirm'], type='http', auth='public', website=True, csrf=True)
    def shipping_details_confirm(self, **post):
        order = request.website.sale_get_order()

        if not order:
            return request.not_found()

        po_number = post.get('purchase_order')
        order_customer = post.get('order_customer')
        order_phone = post.get('order_phone')
        order_address = post.get('order_address')

        # Check if PO number already exists on another order
        existing_order = request.env['sale.order'].sudo().search([
            ('purchase_order', '=', po_number),
            ('id', '!=', order.id)
        ], limit=1)

        if existing_order:
            return request.render('website_sale_lexora.shipping-details', {
                'error': {'purchase_order': 'PO number already exists'},
                'purchase_order': po_number,
                'order_customer': order_customer,
                'order_phone': order_phone,
                'order_address': order_address,
            })

        # ✅ Save purchase_order and other fields
        order.sudo().write({
            'purchase_order': po_number,
            'partner_name': order_customer,
            'partner_phone': order_phone,
            'partner_street': order_address,
        })

        return redirect('/shop/payment')
