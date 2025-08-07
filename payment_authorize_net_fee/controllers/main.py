from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleAuthorizeNetFee(WebsiteSale):

    def payment_transaction(self, **post):
        order = request.website.sale_get_order()
        provider_code = post.get('pm_id') and request.env['payment.provider'].browse(int(post['pm_id'])).code or None

        if order and provider_code == 'authorize_net':
            order.with_context(payment_provider_code=provider_code)._add_authorize_net_fee()

        return super().payment_transaction(**post)
