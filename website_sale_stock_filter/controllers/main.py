# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockFilter(WebsiteSale):

    def _shop_get_product_search_domain(self, search, category, attrib_values):
        # Start with the default domain
        domain = super()._shop_get_product_search_domain(search, category, attrib_values)

        availability = request.params.get('availability')
        if availability == 'available':
            domain += [('qty_available', '>', 0)]
        elif availability == 'not_available':
            domain += [('qty_available', '<=', 0)]

        return domain
