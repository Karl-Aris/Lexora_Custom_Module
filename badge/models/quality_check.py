from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    x_condition_badge = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_badge",
    )

    @api.depends("x_studio_condition")
    def _compute_condition_badge(self):
        for qc in self:
            condition = qc.x_studio_condition or ""
            color = "secondary"
            label = condition

            if condition == "Good":
                color = "success"   # green
            elif condition == "Damaged":
                color = "danger"    # red
            elif condition == "Partial Return":
                color = "secondary" # gray

            qc.x_condition_badge = (
                f'<span class="badge rounded-pill text-bg-{color}">{label}</span>'
            )
