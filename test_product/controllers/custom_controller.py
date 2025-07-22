from odoo import http
from odoo.http import request

class WebsiteCustomController(http.Controller):

    @http.route(['/store'], type='http', auth='public', website=True)
    def search_by_sku(self, **kwargs):
        return request.render('custom_configuration.custom_page_template')
    
    @http.route(['/store/button'], type='http', auth='public', website=True)
    def search_by_sku(self, **kwargs):
        return request.redirect('/store')