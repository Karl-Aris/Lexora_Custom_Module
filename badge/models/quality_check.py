from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_status_html = fields.Html(
        string="Condition Status",
        compute="_compute_condition_status_html",
    )

    @api.depends("x_studio_condition")
    def _compute_condition_status_html(self):
        for qc in self:
            label = qc.x_studio_condition or ""
            color = "secondary"

            if label == "Good":
                color = "success"  # green
            elif label == "Damaged":
                color = "danger"  # red
            elif label == "Partial Return":
                color = "warning"  # yellow/orange

            qc.condition_status_html = (
                f'<span class="badge rounded-pill text-bg-{color}">{label}</span>'
                if label else ""
            )
