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
            label = ""
            color = "secondary"

            if qc.x_studio_condition == "Good":
                label = "Good"
                color = "success"  # green
            elif qc.x_studio_condition == "Damaged":
                label = "Damaged"
                color = "danger"  # red
            elif qc.x_studio_condition == "Partial Return":
                label = "Partial Return"
                color = "warning"  # yellow/orange

            if label:
                qc.condition_status_html = (
                    f'<span class="badge rounded-pill text-bg-{color}">'
                    f"{label}</span>"
                )
            else:
                qc.condition_status_html = ""
