from odoo import models, fields

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_badge_html = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_badge_html",
        sanitize=False,
        store=False,
    )

    def _compute_condition_badge_html(self):
        for rec in self:
            if rec.x_studio_condition:
                rec.condition_badge_html = (
                    f'<span class="badge rounded-pill text-bg-info">{rec.x_studio_condition}</span>'
                )
            else:
                rec.condition_badge_html = ""
