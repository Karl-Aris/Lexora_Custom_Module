from odoo import models, fields

class GoogleSheetEmbed(models.Model):
    _name = 'google.sheet.embed'
    _description = 'Google Sheet Embed'

    name = fields.Char(required=True)
    x_studio_embedded_google_sheet = fields.Html("Embedded Google Sheet", sanitize=False)
