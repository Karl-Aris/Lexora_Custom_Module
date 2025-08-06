from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string='Purchase Order')  # Use Char instead of Many2one
    x_picking_in = fields.Char(string='Picking IN')
    x_delivery_out = fields.Char(string='Delivery OUT')

    @api.model
    def create(self, vals):
        order = super().create(vals)
        order._auto_assign_pickings()
        return order

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            record._auto_assign_pickings()
        return res

    def _auto_assign_pickings(self):
        for r in self:
            if not r.purchase_order or (r.x_picking_in and r.x_delivery_out):
                continue

            # Match by PO name
            pickings = self.env['stock.picking'].search([
                ('origin', '=', r.purchase_order),
                ('name', 'ilike', 'WH/%')
            ])

            vals = {}

            if not r.x_picking_in:
                picking_in = next((p for p in pickings if 'WH/PICK' in p.name), None)
                if picking_in:
                    vals['x_picking_in'] = picking_in.name

            if not r.x_delivery_out:
                picking_out = next((p for p in pickings if 'WH/OUT' in p.name), None)
                if picking_out:
                    vals['x_delivery_out'] = picking_out.name

            if vals:
                r.write(vals)
