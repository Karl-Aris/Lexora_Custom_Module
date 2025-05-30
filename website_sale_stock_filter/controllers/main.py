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
        _logger.info("[LOG] Availability selected: %s", availability)

        response = super().shop(page=page, category=category, search=search, **post)
        products = response.qcontext.get('products')

        if products:
            products = products.sudo()
            _logger.info("[LOG] Initial products count: %d", len(products))
            _logger.info("[LOG] Product IDs before filtering: %s", products.mapped('id'))

            if availability == 'available':
                products = products.filtered(lambda p: p.qty_available > 0)
                _logger.info("[LOG] Filtered (available) products: %s", products.mapped('id'))
            elif availability == 'not_available':
                products = products.filtered(lambda p: p.qty_available <= 0)
                _logger.info("[LOG] Filtered (not available) products: %s", products.mapped('id'))

            response.qcontext['products'] = products

        return response
