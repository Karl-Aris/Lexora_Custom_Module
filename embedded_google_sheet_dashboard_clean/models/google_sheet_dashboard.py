
from odoo import models, fields, api

class EmbeddedGoogleSheetDashboard(models.Model):
    _name = 'embedded.google.sheet.dashboard'
    _description = 'Embedded Google Sheet Dashboard'
    _inherit = []

    name = fields.Char(string="Dashboard Name", required=True)
    google_sheet_url = fields.Char(string="Google Sheet URL")
    embedded_google_sheet = fields.Html(string="Embedded Google Sheet", compute="_compute_embed_html", store=True)

    @api.depends('google_sheet_url')
    def _compute_embed_html(self):
        for rec in self:
            if rec.google_sheet_url:
                embed_url = rec.google_sheet_url.replace('/edit', '/pubhtml?widget=true&headers=false')
                rec.embedded_google_sheet = f'<iframe src="{embed_url}" width="100%" height="800" frameborder="0" allowfullscreen="true"></iframe>'
            else:
                rec.embedded_google_sheet = ''
