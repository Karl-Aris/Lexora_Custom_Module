from odoo import models, fields, api

class CustomStockMoveLine(models.Model):
    _name = 'custom.stock.move.line'
    _description = 'Custom Stock Move Line'
    _inherits = {'stock.move.line': 'move_line_id'}

    move_line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade', string="Stock Move Line")

    x_custom_field = fields.Char(string="Custom Field")
    x_custom_note = fields.Text(string="Custom Note")
    x_computed_field = fields.Float(string="Computed Field", compute='_compute_custom_value')

    # Related fields for views
    product_id = fields.Many2one(related='move_line_id.product_id', string='Product', readonly=True)
    product_uom_qty = fields.Float(related='move_line_id.product_uom_qty', string='Quantity', readonly=True)
    quantity_done = fields.Float(related='move_line_id.quantity_done', string='Done', readonly=True)

    @api.depends('move_line_id.product_uom_qty', 'move_line_id.quantity_done')
    def _compute_custom_value(self):
        for record in self:
            record.x_computed_field = record.move_line_id.product_uom_qty - record.move_line_id.quantity_done
