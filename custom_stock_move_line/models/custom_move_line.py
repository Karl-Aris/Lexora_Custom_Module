from odoo import models, fields, api

class CustomStockMoveLine(models.Model):
    _name = 'custom.stock.move.line'
    _description = 'Custom Stock Move Line'
    _inherits = {'stock.move.line': 'move_line_id'}

    move_line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade', string="Stock Move Line")

    # Custom fields
    x_custom_field = fields.Char(string="Custom Field")
    x_custom_note = fields.Text(string="Custom Note")

    # Computed field example
    x_computed_field = fields.Float(string="Computed Field", compute='_compute_custom_value')

    @api.depends('product_uom_qty', 'quantity_done')
    def _compute_custom_value(self):
        for record in self:
            record.x_computed_field = record.product_uom_qty - record.quantity_done
