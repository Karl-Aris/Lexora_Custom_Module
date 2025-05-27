from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleAvailabilityFilter(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description)

        availability = request.params.get('availability')

        if availability == 'available':
            domain += [('product_variant_ids.qty_available', '>', 0)]
        elif availability == 'unavailable':
            domain += [('product_variant_ids.qty_available', '=', 0)]

        return domain
