from odoo import http
from odoo.http import request

class GoogleSheetController(http.Controller):
    @http.route(['/my_google_sheet/<int:dashboard_id>'], auth='user', type='http', website=True)
    def show_sheet(self, dashboard_id):
        dashboard = request.env['report.dashboard'].browse(dashboard_id)
        return request.render('embedded_google_sheet_dashboard_clean.google_sheet_template', {'dashboard': dashboard})
