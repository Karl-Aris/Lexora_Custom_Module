from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):

    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)

        # Get a specific internal location ID (e.g., main warehouse stock location)
        stock_location = request.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('name', 'ilike', 'WH')  # Replace with your actual stock location name if needed
        ], limit=1)

        if stock_location:
            # Fetch product.template IDs that have qty > 0 in this location
            query = """
                SELECT product_id
                FROM stock_quant
                WHERE location_id = %s AND quantity > 0
            """
            request.env.cr.execute(query, (stock_location.id,))
            product_ids = [row[0] for row in request.env.cr.fetchall()]

            if product_ids:
                domain += [('product_variant_ids', 'in', product_ids)]
            else:
                domain += [('id', '=', 0)]  # Force empty results if no stock

        return domain
