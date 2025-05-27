from odoo import http
from odoo.addons.website_sale.controllers import main as website_sale_main
from odoo.http import request


class WebsiteSaleWithAvailabilityFilter(website_sale_main.WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)

        availability_filters = request.params.getlist('availability')
        if availability_filters:
            # If filtering for 'available' products only
            if 'available' in availability_filters:
                domain.append(('qty_available', '>', 0))
            # If filtering for 'not_available' products only
            if 'not_available' in availability_filters:
                domain.append(('qty_available', '=', 0))

            # If both selected, show all products (remove availability filter)
            if 'available' in availability_filters and 'not_available' in availability_filters:
                # Remove any availability filters (optional, already no effect)
                pass

        return domain