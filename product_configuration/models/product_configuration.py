from odoo import http
from odoo.http import request

class WebsiteInventoryController(http.Controller):

    @http.route(['/test-shop'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        if sku:
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

        return request.render('website_inventory_sku_search.product_sku_page', {
            'product': product,
            'sku': sku,
        })