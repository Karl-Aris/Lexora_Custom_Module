from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo import http

class WebsiteSaleCustom(WebsiteSale):

    @route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def shop_payment_validate(self, **post):
        response = super().shop_payment_validate(**post)

        sale_order = request.website.sale_get_order()
        if not sale_order:
            return response

        # Check last transaction
        tx = sale_order.transaction_ids.filtered(lambda t: t.state in ['pending', 'authorized', 'done'])[:1]
        if tx and tx.provider_id.code == 'authorize':
            if tx.state != 'done':
                # Redirect to a "processing" or error page if not completed
                return request.redirect('/shop/payment/pending')

        return response

    @route(['/shop/payment/pending'], type='http', auth="public", website=True, sitemap=False)
    def payment_pending_page(self):
        return request.render("payment_authorize_net_fee.template_payment_pending", {})
