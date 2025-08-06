from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_picking_in = fields.Char(string="Picking IN", readonly=True)
    x_delivery_out = fields.Char(string="Delivery OUT", readonly=True)

    @api.model
    def create(self, vals):
        order = super().create(vals)
        order._set_picking_refs()
        return order

    def write(self, vals):
        res = super().write(vals)
        if any(field in vals for field in ['purchase_order']):
            for order in self:
                order._set_picking_refs()
        return res

    def _set_picking_refs(self):
        for record in self:
            if not record.purchase_order:
                continue

            # Search both pickings in a single query
            pickings = self.env['stock.picking'].search([
                ('purchase_order', '=', record.purchase_order),
                ('name', 'ilike', 'WH/%')
            ])

            vals = {}
            # Filter matching pickings once
            pick_dict = {p.name: p.name for p in pickings}

            if not record.x_picking_in:
                vals['x_picking_in'] = next((name for name in pick_dict if 'WH/PICK' in name), False)

            if not record.x_delivery_out:
                vals['x_delivery_out'] = next((name for name in pick_dict if 'WH/OUT' in name), False)

            if vals:
                record.write(vals)
