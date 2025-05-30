# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleStockFilter(WebsiteSale):

    @http.route(['/shop'], type='http', auth="public", website=True, sitemap=True)
    def shop(self, page=0, category=None, search='', **post):
        availability = post.get('availability')
        _logger.info("Availability filter selected: %s", availability)

        response = super().shop(page=page, category=category, search=search, **post)
        products = response.qcontext.get('products')

        if products and availability:
            products = products.sudo()
            _logger.info("Initial product count before filtering: %d", len(products))

            if availability == 'available':
                products = products.filtered(lambda p: p.qty_available > 0)
                _logger.info("Filtered to %d products with qty > 0", len(products))
            elif availability == 'not_available':
                products = products.filtered(lambda p: p.qty_available <= 0)
                _logger.info("Filtered to %d products with qty <= 0", len(products))

            # Optional: Log product IDs that passed filter
            _logger.debug("Filtered product IDs: %s", products.ids)

            response.qcontext['products'] = products

        return response
