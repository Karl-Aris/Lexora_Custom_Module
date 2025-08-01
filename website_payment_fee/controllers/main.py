from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsitePaymentFee(WebsiteSale):
    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def shop_payment(self, **post):
        """Intercept payment method selection and tag the sale.order"""
        response = super().shop_payment(**post)

        order = request.website.sale_get_order()
        provider = post.get('provider')

        if order and provider:
            order.sudo().write({'x_payment_provider_code': provider})

        return response
