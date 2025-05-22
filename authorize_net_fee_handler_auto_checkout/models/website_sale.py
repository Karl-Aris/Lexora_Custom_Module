
from odoo import models

class WebsiteSale(models.Model):
    _inherit = 'website_sale'

    def _place_order(self, **kwargs):
        order = super()._place_order(**kwargs)
        if order.payment_provider_id and order.payment_provider_id.code == 'authorize_net':
            order.add_authorize_net_surcharge()
        return order
