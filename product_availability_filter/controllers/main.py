from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockFiltered(WebsiteSale):

    def _get_product_domain(self, search, category, attrib_values):
        domain = super()._get_product_domain(search, category, attrib_values)
        availability = request.params.get('availability')

        if availability in ['available', 'not_available']:
            # Target location (adjust name/path as needed)
            location = request.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('complete_name', '=', 'WH/Stock')
            ], limit=1)

            if location:
                # Get all product ids and their available quantity in that location
                quant = request.env['stock.quant'].read_group(
                    [('location_id', '=', location.id)],
                    ['product_id', 'quantity:sum'],
                    ['product_id']
                )
                product_quant_map = {q['product_id'][0]: q['quantity'] for q in quant}

                if availability == 'available':
                    available_ids = [pid for pid, qty in product_quant_map.items() if qty > 0]
                    domain += [('id', 'in', available_ids)]
                else:  # not_available
                    all_product_ids = request.env['product.product'].search([]).ids
                    available_ids = [pid for pid, qty in product_quant_map.items() if qty > 0]
                    domain += [('id', 'not in', available_ids)]

        return domain
