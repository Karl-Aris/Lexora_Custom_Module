from odoo import models, fields

class ReturnsReport(models.Model):
    _name = "returns.report"
    _description = "Returns Report"
    _inherits = {"stock.move.line": "move_line_id"}  # Delegation inheritance

    move_line_id = fields.Many2one(
        "stock.move.line",
        string="Stock Move Line",
        required=True,
        ondelete="cascade",
    )

    # Custom fields
    return_reason = fields.Text(string="Reason for Return")
    approved_by = fields.Many2one("res.users", string="Approved By")
    is_processed = fields.Boolean(string="Processed", default=False)
