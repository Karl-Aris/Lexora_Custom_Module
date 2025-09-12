from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_status_html = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_status_html",
        store=False,
    )

    @api.depends("x_studio_condition")
    def _compute_condition_status_html(self):
        for record in self:
            label = record.x_studio_condition or ""
            color = "secondary"  # default gray

            if label.lower() == "good":
                color = "success"  # green
            elif label.lower() == "damaged":
                color = "danger"   # red
            elif label.lower() == "partial return":
                color = "secondary"  # gray

            record.condition_status_html = (
                f'<span class="badge rounded-pill text-bg-{color}">{label}</span>'
            )
