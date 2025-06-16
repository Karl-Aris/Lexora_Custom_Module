from odoo import http
from odoo.http import request

class GoogleSheetController(http.Controller):

    @http.route('/google-sheet', auth='public', website=True)
    def show_google_sheet(self):
        iframe_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ.../pubhtml?widget=true&amp;headers=false"
        return request.render('google_sheet_embed.sheet_embed_template', {
            'iframe_url': iframe_url
        })
