from odoo import models, fields, api

class XReport(models.Model):
    _name = 'x_report'
    _description = 'Custom Report'

    x_name = fields.Char()
    x_google_url = fields.Char(string="Google Sheet URL")
    x_iframe = fields.Html(string="Embedded Iframe", compute='_compute_iframe', sanitize=False)

    @api.depends('x_google_url')
    def _compute_iframe(self):
        for rec in self:
            if rec.x_google_url:
                rec.x_iframe = f"""
                    <iframe src="{rec.x_google_url}"
                            width="100%" height="600" frameborder="0" allowfullscreen>
                    </iframe>
                """
            else:
                rec.x_iframe = False
