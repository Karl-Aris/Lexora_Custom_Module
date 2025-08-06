from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_picking_in = fields.Char(string='Picking IN')
    x_delivery_out = fields.Char(string='Delivery OUT')

    @api.model
    def create(self, vals):
        order = super().create(vals)
        order._update_picking_references()
        return order

    def write(self, vals):
        res = super().write(vals)
        self._update_picking_references()
        return res

    def _update_picking_references(self):
        for r in self:
            if not r.purchase_order or (r.x_picking_in and r.x_delivery_out):
                continue

            related_pickings = self.env['stock.picking'].search([
                ('purchase_order', '=', r.purchase_order),
                ('name', 'ilike', 'WH/%'),
            ])

            vals = {}

            if not r.x_picking_in:
                picking_in = next((p for p in related_pickings if 'WH/PICK' in p.name), None)
                if picking_in:
                    vals['x_picking_in'] = picking_in.name

            if not r.x_delivery_out:
                picking_out = next((p for p in related_pickings if 'WH/OUT' in p.name), None)
                if picking_out:
                    vals['x_delivery_out'] = picking_out.name

            if vals:
                r.write(vals)
