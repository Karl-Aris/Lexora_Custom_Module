from odoo import models, fields, api

class CustomStockMoveLine(models.Model):
    _name = 'custom.stock.move.line'
    _description = 'Custom Stock Move Line'
    _inherits = {'stock.move.line': 'move_line_id'}

    move_line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade')

    x_custom_field = fields.Char(string="Custom Field")
    x_custom_note = fields.Text(string="Custom Note")
    x_computed_field = fields.Float(string="Computed Field", compute='_compute_custom_value')

    # Related fields
    product_id = fields.Many2one('product.product', string="Product", related='move_line_id.product_id', store=True)
    product_uom_qty = fields.Float(string="Ordered Quantity", related='move_line_id.product_uom_qty', store=True)
    quantity_done = fields.Float(string="Done Quantity", related='move_line_id.quantity_done', store=True)

    @api.depends('product_uom_qty', 'quantity_done')
    def _compute_custom_value(self):
        for record in self:
            record.x_computed_field = record.product_uom_qty - record.quantity_done
