from odoo import models, fields

class GoogleSheetEmbed(models.Model):
    _name = 'google.sheet.embed'
    _description = 'Google Sheet Embed'

    name = fields.Char(string="Title")
    iframe_html = fields.Html(string="Iframe HTML", sanitize=False)
