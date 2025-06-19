from odoo import models, fields, api

class ReportDashboard(models.Model):
    _name = 'report.dashboard'
    _description = 'Google Sheet Dashboard'

    name = fields.Char(required=True)
    google_sheet_url = fields.Char()
    embedded_google_sheet = fields.Html(compute="_compute_embed", store=True)

    @api.depends('google_sheet_url')
    def _compute_embed(self):
        for rec in self:
            url = rec.google_sheet_url or ""
            if "/edit" in url:
                embed_url = url.replace("/edit", "/pubhtml?widget=true&headers=false")
            elif "/pubhtml" in url and "widget=true" not in url:
                embed_url = url + "?widget=true&headers=false"
            else:
                embed_url = url
            rec.embedded_google_sheet = (
                f'<iframe src="{embed_url}" width="100%" height="800" frameborder="0" allowfullscreen></iframe>' if embed_url else ''
            )
