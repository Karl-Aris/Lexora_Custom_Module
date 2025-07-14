# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class WebsiteSaleLexora(http.Controller):

    @http.route(['/shop/shipping-details/confirm'], type='http', auth="public", website=True, csrf=True)
    def lexora_shipping_details_confirm(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop')

        # Extract posted data
        purchase_order = post.get('purchase_order', '').strip()

        # Duplicate PO# Check
        if purchase_order:
            existing = request.env['sale.order'].sudo().search([
                ('client_order_ref', '=', purchase_order),
                ('id', '!=', order.id)
            ], limit=1)
            if existing:
                error = {'purchase_order': 'Duplicate PO# found'}
                return request.render('website_sale_lexora.shipping-details', {
                    'error': error,
                    'purchase_order': purchase_order
                })

        # Assign PO# to sale.order
        if purchase_order:
            order.sudo().write({'client_order_ref': purchase_order})

        return request.redirect('/shop/payment')
