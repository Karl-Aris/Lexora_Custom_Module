from odoo import http
from odoo.http import request

class WebsiteCustomController(http.Controller):

    @http.route(['/custom_test2'], type='http', auth='public', website=True)
    def render_custom_test2(self, **kwargs):
        return request.render('test_product.custom_page_template')

    @http.route(['/custom_test2/button'], type='http', auth='public', website=True)
    def button_redirect(self, **kwargs):
        return request.redirect('/custom_test2')
    
    @http.route(['/custom_test2/search_sku'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        if sku:
            product = request.env['product.template'].sudo().search([('default_code', '=', sku)], limit=1)

        return request.render('test_product.custom_page_template', {
            'product': product,
            'sku': sku,
        })
