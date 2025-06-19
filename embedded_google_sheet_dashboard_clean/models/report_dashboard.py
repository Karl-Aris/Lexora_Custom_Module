from odoo import models, fields, api

class ReportDashboard(models.Model):
    _name = 'report.dashboard'
    _description = 'Google Sheet Dashboard'

    name = fields.Char(required=True)
    google_sheet_url = fields.Char(string="Google Sheet URL")

    embedded_google_sheet = fields.Html(string="Embedded Sheet", compute="_compute_embedded_google_sheet", sanitize=False)

    @api.depends('google_sheet_url')
    def _compute_embedded_google_sheet(self):
        for rec in self:
            if rec.google_sheet_url:
                rec.embedded_google_sheet = f"""
                    <iframe src="{rec.google_sheet_url}" width="100%" height="1400px" frameborder="0" allowfullscreen></iframe>
                """
            else:
                rec.embedded_google_sheet = "<p>No sheet URL provided.</p>"
