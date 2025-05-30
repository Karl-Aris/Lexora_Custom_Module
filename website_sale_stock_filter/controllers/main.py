# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):

    @http.route(['/shop'], type='http', auth="public", website=True, sitemap=True)
    def shop(self, page=0, category=None, search='', **post):
        response = super().shop(page=page, category=category, search=search, **post)

        availability = post.get('availability')
        products = response.qcontext.get('products')

        if products:
            # Auto publish/unpublish based on stock
            for product in products:
                if product.qty_available > 0 and not product.website_published:
                    product.website_published = True
                elif product.qty_available <= 0 and product.website_published:
                    product.website_published = False

            # Apply filter after publish/unpublish
            if availability == 'available':
                products = products.filtered(lambda p: p.qty_available > 0)
            elif availability == 'not_available':
                products = products.filtered(lambda p: p.qty_available <= 0)

            response.qcontext['products'] = products

        return response
