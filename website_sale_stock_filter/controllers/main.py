from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleStockFiltered(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        # Get the original domain
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description)

        # Add condition: only show products where at least one variant has stock
        domain += [('product_variant_ids.qty_available', '>', 0)]

        return domain
