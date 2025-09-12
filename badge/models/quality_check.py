from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_badge_html = fields.Html(
        string="Condition (HTML)",
        compute="_compute_condition_badge_display",
    )

    condition_text = fields.Char(
        string="Condition (Text)",
        compute="_compute_condition_badge_display",
    )

    @api.depends("x_studio_condition")
    def _compute_condition_badge_display(self):
        for record in self:
            condition = (record.x_studio_condition or "").strip()
            badge_html = ""
            plain_text = condition

            # assign badge color
            if condition.lower() == "good":
                badge_html = (
                    f'<span class="badge rounded-pill text-bg-success">{condition}</span>'
                )
            elif condition.lower() == "damaged":
                badge_html = (
                    f'<span class="badge rounded-pill text-bg-danger">{condition}</span>'
                )
            elif condition.lower() == "partial return":
                badge_html = (
                    f'<span class="badge rounded-pill text-bg-secondary">{condition}</span>'
                )
            else:
                badge_html = (
                    f'<span class="badge rounded-pill text-bg-light">{condition}</span>'
                )

            record.condition_badge_html = badge_html
            record.condition_text = plain_text
