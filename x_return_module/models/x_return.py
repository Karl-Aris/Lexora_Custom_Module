# -*- coding: utf-8 -*-
from odoo import models, fields, api

class XReturn(models.Model):
    _name = 'x.return'
    _description = 'Return Stock Move Line'
    _order = 'id desc'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number')
    package_id = fields.Many2one('stock.quant.package', string='Source Package')
    result_package_id = fields.Many2one('stock.quant.package', string='Destination Package')
    owner_id = fields.Many2one('res.partner', string='Owner')
    location_id = fields.Many2one('stock.location', string='From Location', required=True)
    location_dest_id = fields.Many2one('stock.location', string='To Location', required=True)
    qty_done = fields.Float(string='Quantity Done', default=0.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    reference = fields.Char(string='Reference')

    move_id = fields.Many2one('stock.move', string='Related Stock Move')
    move_line_id = fields.Many2one('stock.move.line', string='Original Move Line')

    name = fields.Char(string='Description', compute='_compute_name', store=True)

    @api.depends('product_id', 'qty_done', 'product_uom_id')
    def _compute_name(self):
        for rec in self:
            if rec.product_id:
                name = rec.product_id.display_name
                uom = rec.product_uom_id.name if rec.product_uom_id else ''
                rec.name = f"{name} - {rec.qty_done} {uom}"
            else:
                rec.name = 'Return Line'

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # Use reference if present, otherwise try to use related picking name
            ref = False
            if hasattr(rec, 'reference') and rec.reference:
                ref = rec.reference
            elif rec.picking_id and getattr(rec.picking_id, 'name', False):
                ref = rec.picking_id.name
            # Only create x.return when reference contains WH/INT/RETURN (case-insensitive)
            if ref and 'WH/INT/RETURN' in ref.upper():
                try:
                    self.env['x.return'].create({
                        'product_id': rec.product_id.id or False,
                        'lot_id': rec.lot_id.id or False,
                        'package_id': rec.package_id.id or False,
                        'result_package_id': rec.result_package_id.id or False,
                        'owner_id': rec.owner_id.id or False,
                        'location_id': rec.location_id.id or False,
                        'location_dest_id': rec.location_dest_id.id or False,
                        'qty_done': rec.qty_done or 0.0,
                        'product_uom_id': rec.product_uom_id.id or False,
                        'reference': ref,
                        'move_id': rec.move_id.id or False,
                        'move_line_id': rec.id,
                    })
                except Exception:
                    # Avoid breaking the create flow if x.return creation fails.
                    # Logging could be added here if desired.
                    pass
        return records
