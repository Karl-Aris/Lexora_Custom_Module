from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAuthorizeNetFee(WebsiteSale):

    def _get_order(self):
        """Override to add fee before payment if Authorize.Net is chosen."""
        order = super()._get_order()
        if order and order.payment_provider_id and order.payment_provider_id.code == 'authorize':
            order._add_authorize_net_fee()
        return order
