from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_pickings_fast()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_pickings_fast()
        return res

    def _update_pickings_fast(self):
        Picking = self.env['stock.picking']
        for rec in self:
            if not rec.purchase_order:
                continue
    
            vals = {}
            domain_base = [('purchase_order', '=', rec.purchase_order)]
    
            if not rec.x_picking_in:
                picking_in = Picking.search(
                    domain_base + [('name', '=like', 'WH/PICK%')],
                    limit=1
                )
                if picking_in:
                    vals['x_picking_in'] = picking_in.name
    
            if not rec.x_delivery_out:
                picking_out = Picking.search(
                    domain_base + [('name', '=like', 'WH/OUT%')],
                    limit=1
                )
                if picking_out:
                    vals['x_delivery_out'] = picking_out.name
    
            if vals:
                rec.write(vals)
