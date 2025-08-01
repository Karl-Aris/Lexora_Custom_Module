from odoo import http
from odoo.http import request

class WebsitePaymentFee(http.Controller):

    @http.route(['/shop/payment'], type='http', auth='public', website=True, sitemap=False)
    def payment(self, **post):
        order = request.website.sale_get_order()
        provider_code = post.get('provider')

        if order and provider_code:
            order = order.sudo()
            order.add_payment_fee_line(provider_code)

        return request.redirect('/shop/payment')
