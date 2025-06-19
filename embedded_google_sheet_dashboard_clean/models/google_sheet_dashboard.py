from odoo import models, fields, api

class ReportDashboard(models.Model):
    _name = 'report.dashboard'
    _description = 'Google Sheet Dashboard'

    name = fields.Char(string="Dashboard Name", required=True)
    google_sheet_url = fields.Char(string="Google Sheet URL")
    embedded_google_sheet = fields.Html(string="Embedded Google Sheet", compute="_compute_embed", store=True)

    @api.depends('google_sheet_url')
    def _compute_embed(self):
        for rec in self:
            if rec.google_sheet_url:
                url = rec.google_sheet_url.replace('/edit', '/pubhtml?widget=true&headers=false')
                rec.embedded_google_sheet = (
                    f'<iframe src="{url}" width="100%" height="800" frameborder="0"></iframe>'
                )
            else:
                rec.embedded_google_sheet = ''
