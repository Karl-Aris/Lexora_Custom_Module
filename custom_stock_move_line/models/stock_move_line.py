from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Example custom field
    x_custom_note = fields.Char(string="Custom Note")

    # Example computed field (optional demo)
    x_qty_double = fields.Float(
        string="Double Quantity",
        compute="_compute_qty_double",
        store=True
    )

    @api.depends('qty_done')
    def _compute_qty_double(self):
        for line in self:
            line.x_qty_double = line.qty_done * 2
