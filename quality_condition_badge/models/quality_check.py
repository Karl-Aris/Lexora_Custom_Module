from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_badge = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_badge",
        sanitize=False,
    )

    @api.depends("x_studio_condition")
    def _compute_condition_badge(self):
        for rec in self:
            value = (rec.x_studio_condition or "").strip().lower()
            if value == "good":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-success">Good</span>'
            elif value == "damaged":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-danger">Damaged</span>'
            elif value == "partial":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-secondary">Partial</span>'
            else:
                rec.condition_badge = '<span class="badge rounded-pill text-bg-light">N/A</span>'
