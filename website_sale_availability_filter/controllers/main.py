# File: website_hide_out_of_stock/controllers/main.py

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFiltered(WebsiteSale):

    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)

        # Only show templates that have at least one variant with virtual_available > 0
        domain.append(('product_variant_ids.virtual_available', '>', 0))

        return domain
