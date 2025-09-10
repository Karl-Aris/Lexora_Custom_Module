from odoo import models, fields, api

class ReturnsReport(models.Model):
    _name = "returns.report"
    _description = "Returns Report"

    move_line_id = fields.Many2one(
        "stock.move.line",
        string="Stock Move Line",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(related="move_line_id.product_id", store=True)
    lot_id = fields.Many2one(related="move_line_id.lot_id", store=True)
    qty_done = fields.Float(related="move_line_id.qty_done", store=True)
    location_id = fields.Many2one(related="move_line_id.location_id", store=True)
    location_dest_id = fields.Many2one(related="move_line_id.location_dest_id", store=True)

    return_reason = fields.Text(string="Reason for Return")
    approved_by = fields.Many2one("res.users", string="Approved By")
    is_processed = fields.Boolean(string="Processed", default=False)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def create_returns_report_if_needed(self):
        """Create or update a returns.report if this move line is a return"""
        for line in self:
            if line.picking_id and line.picking_id.name.startswith("WH/INT/RETURN"):
                report = self.env["returns.report"].search([("move_line_id", "=", line.id)], limit=1)
                if not report:
                    self.env["returns.report"].create({"move_line_id": line.id})

    @api.model
    def create(self, vals):
        records = super().create(vals)
        records.create_returns_report_if_needed()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.create_returns_report_if_needed()
        return res
