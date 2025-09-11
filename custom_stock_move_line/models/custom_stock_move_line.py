from odoo import models, fields, api

class CustomStockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_custom_field = fields.Char(string="Custom Field")
    x_custom_note = fields.Text(string="Custom Note")
    x_computed_field = fields.Float(
        string="Computed Field", compute='_compute_custom_value'
    )

    @api.depends('product_uom_qty', 'quantity_done')
    def _compute_custom_value(self):
        for record in self:
            record.x_computed_field = record.product_uom_qty - record.quantity_done
