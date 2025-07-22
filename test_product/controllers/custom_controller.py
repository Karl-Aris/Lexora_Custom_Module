from odoo import http
from odoo.http import request

class WebsiteCustomController(http.Controller):

    @http.route(['/custom-test2'], type='http', auth='public', website=True)
    def search_by_sku(self, **kwargs):
        return request.render('custom_configuration.custom_page_template')
    
    @http.route(['/custom-test2/button'], type='http', auth='public', website=True)
    def search_by_sku(self, **kwargs):
        return request.redirect('/store')
