from odoo import http
from odoo.http import request

class WebsitePaymentFeeController(http.Controller):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/shop/cart")

        provider_id = post.get('provider_id')
        if provider_id:
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if provider.code == 'authorize':
                order._add_payment_fee_line()
        return request.redirect("/shop/payment")
