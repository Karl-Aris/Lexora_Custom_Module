from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleStockFilter(WebsiteSale):
    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)
        try:
            domain += [('product_variant_ids.qty_available', '>', 0)]
        except Exception as e:
            # Log the issue for debugging
            _logger = request.env['ir.logging']
            _logger.create({
                'name': 'Stock Filter Error',
                'type': 'server',
                'level': 'error',
                'message': f'Stock domain error: {e}',
                'path': 'website_sale_stock_filter',
                'func': '_shop_get_product_domain',
                'line': 0,
            })
        return domain
