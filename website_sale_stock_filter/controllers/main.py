from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)

        # Add logic to show only products with positive available quantity
        in_stock_product_templates = http.request.env['product.template'].search([
            ('type', '=', 'product'),
            ('website_published', '=', True),
        ])

        # Filter templates with stock
        in_stock_ids = []
        for template in in_stock_product_templates:
            if any(variant.qty_available > 0 for variant in template.product_variant_ids):
                in_stock_ids.append(template.id)

        domain += [('id', 'in', in_stock_ids)]
        return domain
