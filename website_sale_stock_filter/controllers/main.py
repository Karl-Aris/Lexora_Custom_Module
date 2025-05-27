from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)

        # Only show products that are published and have stock in at least one variant
        domain += [
            ('product_variant_ids.qty_available', '>', 0)
        ]
        return domain
