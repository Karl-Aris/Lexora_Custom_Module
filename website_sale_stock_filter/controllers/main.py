from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):

    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)

        # Step 1: Find location 8 and all its child locations
        location_id = 8
        location_ids = request.env['stock.location'].search([('id', 'child_of', location_id)]).ids

        # Step 2: Find product templates with stock > 0 in any of those locations
        query = """
            SELECT pt.id
            FROM product_template pt
            JOIN product_product pp ON pp.product_tmpl_id = pt.id
            JOIN stock_quant sq ON sq.product_id = pp.id
            WHERE sq.location_id = ANY(%s) AND sq.quantity > 0
            GROUP BY pt.id
        """
        request.env.cr.execute(query, (location_ids,))
        in_stock_product_template_ids = [row[0] for row in request.env.cr.fetchall()]

        # Step 3: Apply the domain filter
        if in_stock_product_template_ids:
            domain += [('id', 'in', in_stock_product_template_ids)]
        else:
            domain += [('id', '=', 0)]  # If nothing in stock, show nothing

        return domain
