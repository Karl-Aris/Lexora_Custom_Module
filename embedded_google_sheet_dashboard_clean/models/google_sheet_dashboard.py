from odoo import models, fields, api

class Report(models.Model):
    _inherit = 'x_report'  # Inherit your studio model

    x_google_sheet_url = fields.Char(string="Google Sheet URL")
    x_studio_embedded_google_sheet = fields.Html(string="Embedded Google Sheet", compute="_compute_embed_sheet", store=True)

    @api.depends('x_google_sheet_url')
    def _compute_embed_sheet(self):
        for record in self:
            if record.x_google_sheet_url:
                sheet_url = record.x_google_sheet_url.replace('/edit', '/pubhtml?widget=true&headers=false')
                record.x_studio_embedded_google_sheet = f'<iframe src="{sheet_url}" width="100%" height="800" frameborder="0"></iframe>'
            else:
                record.x_studio_embedded_google_sheet = ''
