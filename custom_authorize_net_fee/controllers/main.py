from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleAuthorizeFee(http.Controller):

    @http.route(['/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def website_payment_transaction(self, **kwargs):
        order = request.website.sale_get_order()
        if not order or order.state not in ['draft', 'sent']:
            _logger.warning("No active sale order or invalid state for fee injection.")
            return request.redirect('/shop/checkout')

        provider_id = kwargs.get('provider_id')
        if provider_id:
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if provider.code == 'authorize_net':
                if not order.authorize_fee_applied:
                    _logger.info("Injecting Authorize.Net fee into order %s", order.name)
                    order.apply_authorize_net_fee()

        return request.redirect('/shop/payment/transaction/submit?' + http.url_encode(kwargs))
