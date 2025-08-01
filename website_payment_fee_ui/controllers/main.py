# controllers/main.py
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo import http

class WebsiteSaleWithFee(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        response = super().payment(**post)
        order = request.website.sale_get_order()
        if not order:
            return response

        provider_id = int(post.get('payment_option_id', 0))
        provider = request.env['payment.provider'].sudo().browse(provider_id)

        if provider and provider.fee_percentage and provider.fee_product_id:
            order._remove_existing_fee_line(provider.fee_product_id)
            order._add_payment_fee_line(provider.fee_product_id, provider.fee_percentage)

        return response
