from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):

    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)

        # Get the internal stock location (adjust name if needed)
        stock_location = request.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('name', 'ilike', 'Stock')  # Replace "Stock" with exact name if needed
        ], limit=1)

        if stock_location:
            # SQL to get product.template IDs whose variants have stock in that location
            query = """
                SELECT pt.id
                FROM product_template pt
                JOIN product_product pp ON pp.product_tmpl_id = pt.id
                JOIN stock_quant sq ON sq.product_id = pp.id
                WHERE sq.location_id = %s AND sq.quantity > 0
                GROUP BY pt.id
            """
            request.env.cr.execute(query, (stock_location.id,))
            product_tmpl_ids = [row[0] for row in request.env.cr.fetchall()]

            if product_tmpl_ids:
                domain += [('id', 'in', product_tmpl_ids)]
            else:
                domain += [('id', '=', 0)]  # Return nothing if no stock
        else:
            domain += [('id', '=', 0)]  # Safe default if no location found

        return domain
