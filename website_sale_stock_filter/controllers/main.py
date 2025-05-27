from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleStockFiltered(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description)

        # Only include templates where at least one variant has stock
        in_stock_variant_ids = request.env['product.product'].search([('qty_available', '>', 0)]).ids
        domain += [('product_variant_ids', 'in', in_stock_variant_ids)]

        return domain
