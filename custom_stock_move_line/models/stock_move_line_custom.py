from odoo import models, fields, api

class StockMoveLineCustom(models.Model):
    _name = 'stock.move.line.custom'  # new model
    _description = 'Custom Stock Move Line'
    _inherit = 'stock.move.line'         # inherit fields and methods from stock.move.line

    # Custom fields for this new model
    x_custom_note = fields.Char('Custom Note')
    x_qty_double = fields.Float('Double Quantity', compute='_compute_qty_double', store=True)

    @api.depends('qty_done')
    def _compute_qty_double(self):
        for line in self:
            line.x_qty_double = line.qty_done * 2
