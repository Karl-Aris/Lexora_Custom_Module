from odoo import http
from odoo.http import request

class WebsiteCustomController(http.Controller):

    @http.route(['/custom_test2'], type='http', auth='public', website=True)
    def custom_test2(self, **kwargs):
        return request.render('test_product.custom_page_template')
    
    @http.route(['/custom_test2/button'], type='http', auth='public', website=True)
    def custom_test2(self, **kwargs):
        return request.redirect('/custom_test2')
