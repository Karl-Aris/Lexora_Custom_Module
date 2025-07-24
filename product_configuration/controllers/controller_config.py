from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store'], type='http', auth='public', website=True)
    def render_product(self, **kwargs):
        return request.render('product_configuration.template_product_configuration')

    # @http.route(['/store/button'], type='http', auth='public', website=True)
    # def button_redirect(self, **kwargs):
    #     return request.redirect('/custom_test2')
    
    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        if sku:
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'sku': sku,
        })