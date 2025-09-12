from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = "quality.check"

    condition_badge = fields.Html(
        string="Condition Badge",
        compute="_compute_condition_badge",
        sanitize=False,
    )

    @api.depends("quality_state")
    def _compute_condition_badge(self):
        for rec in self:
            value = rec.quality_state or "none"
            if value == "pass":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-success">Good</span>'
            elif value == "fail":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-danger">Damaged</span>'
            elif value == "none":
                rec.condition_badge = '<span class="badge rounded-pill text-bg-warning">Partial Return</span>'
            else:
                rec.condition_badge = '<span class="badge rounded-pill text-bg-light">N/A</span>'
