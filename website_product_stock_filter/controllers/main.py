from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):

    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)

        availability = http.request.params.getlist('availability[]')
        filters = availability if availability else []

        if filters and 'available' in filters and 'not_available' not in filters:
            domain.append(('product_variant_ids.virtual_available', '>', 0))
        elif filters and 'not_available' in filters and 'available' not in filters:
            domain.append(('product_variant_ids.virtual_available', '<=', 0))

        return domain
