from odoo import http
from odoo.http import request

class WebsiteSaleLexora(http.Controller):

    @http.route(['/shop/shipping-details/confirm'], type='http', auth="public", website=True, csrf=True)
    def shipping_details_confirm(self, **post):
        error = {}
        purchase_order = post.get('purchase_order', '').strip()

        # Check if purchase_order already exists
        if purchase_order:
            existing_order = request.env['sale.order'].sudo().search([('purchase_order', '=', purchase_order)], limit=1)
            if existing_order:
                error['purchase_order'] = 'This PO # already exists.'

        required_fields = ['order_customer', 'order_phone', 'order_address']
        for field in required_fields:
            if not post.get(field):
                error[field] = "This field is required."

        if error:
            return request.render("website_sale_lexora.shipping-details", {
                'error': error,
                'purchase_order': purchase_order,
                'order_customer': post.get('order_customer', ''),
                'order_phone': post.get('order_phone', ''),
                'order_address': post.get('order_address', ''),
            })

        sale_order = request.env['sale.order'].sudo().create({
            'purchase_order': purchase_order,
            'partner_id': request.env.user.partner_id.id,
        })

        return request.redirect('/shop/confirmation')
