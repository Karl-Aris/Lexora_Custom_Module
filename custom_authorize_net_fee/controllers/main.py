from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleAuthorizeFee(http.Controller):

    @http.route(['/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def website_payment_transaction(self, **kwargs):
        """
        Intercepts the normal flow before payment transaction is created.
        Adds Authorize.Net fee to the order if it's the selected provider.
        """
        order = request.website.sale_get_order()
        if not order or order.state != 'draft':
            return request.redirect('/shop/checkout')

        provider_id = kwargs.get('provider_id')
        if provider_id:
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if 'authorize' in provider.code:
                _logger.info("Injecting Authorize.Net fee into order %s", order.name)
                order.add_authorize_net_fee()

        # Continue to standard flow
        return request.redirect('/shop/payment/transaction/submit?' + http.url_encode(kwargs))
