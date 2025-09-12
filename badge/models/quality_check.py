from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_badge = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_badge",
        sanitize=False
    )

    @api.depends("x_studio_condition")
    def _compute_condition_badge(self):
        for rec in self:
            color = "secondary"  # default gray
            if rec.x_studio_condition == "Good":
                color = "success"
            elif rec.x_studio_condition == "Damaged":
                color = "danger"

            rec.condition_badge = f"""
                <span class="badge bg-{color}">
                    {rec.x_studio_condition or ''}
                </span>
            """
