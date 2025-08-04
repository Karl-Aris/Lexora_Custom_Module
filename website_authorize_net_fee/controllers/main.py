from odoo import http
from odoo.http import request

class WebsiteSaleAuthorizeFee(http.Controller):

    @http.route(['/update_authnet_fee'], type='json', auth='public', website=True)
    def update_authnet_fee(self, add_fee=False):
        order = request.website.sale_get_order()
        if order:
            order.sudo().update_authorize_net_fee(add_fee)
        return {'status': 'ok'}
