from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store'], type='http', auth='public', website=True)
    def render_product(self, **kwargs):
        return request.render('product_configuration.template_product_configuration')

    
    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        related_sizes = []

        if sku:
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            if product and product.product_tmpl_id.collection_id:
                collection_id = product.product_tmpl_id.collection_id.id
                # Find all variants from other products in same collection
                related_products = request.env['product.product'].sudo().search([
                    ('product_tmpl_id.collection_id', '=', collection_id)
                ])

                # Exclude current SKU if you want
                related_sizes = related_products.filtered(lambda p: p.id != product.id)

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'sku': sku,
        })
