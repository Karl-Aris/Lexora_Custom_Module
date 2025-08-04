from odoo import http
from odoo.http import request

class WebsiteSaleAuthorizeFee(http.Controller):

    @http.route(['/shop/payment/authorize_net_fee'], type='json', auth="public", website=True)
    def set_authorize_net_fee(self, **kw):
        order = request.website.sale_get_order()
        if order:
            order.add_authorize_net_fee()
            return {'status': 'success'}
        return {'status': 'no_order'}
