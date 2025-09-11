from odoo import models, fields

class CustomStockMoveLine(models.Model):
    _name = 'custom.stock.move.line'
    _description = 'Custom Stock Move Line'
    _inherits = {'stock.move.line': 'move_line_id'}

    move_line_id = fields.Many2one(
        'stock.move.line',
        required=True,
        ondelete='cascade',
        string="Stock Move Line"
    )

    x_custom_field = fields.Char(string="Custom Field")
    x_custom_note = fields.Text(string="Custom Note")

    # Use store=False to avoid install-time dependency issues
    x_computed_field = fields.Float(
        string="Computed Field",
        compute='_compute_custom_value',
        store=False
    )

    def _compute_custom_value(self):
        for record in self:
            if record.move_line_id:
                record.x_computed_field = (
                    record.move_line_id.product_uom_qty - record.move_line_id.quantity_done
                )
            else:
                record.x_computed_field = 0.0
