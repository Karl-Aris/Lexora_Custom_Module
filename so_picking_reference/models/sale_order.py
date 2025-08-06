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
        for rec in self:
            if not rec.purchase_order:
                continue

            # Only update if at least one of the Studio fields is empty
            if rec.x_picking_in and rec.x_delivery_out:
                continue

            # Fetch only required fields to speed up lookup
            related_pickings = self.env['stock.picking'].search_read(
                [('purchase_order', '=', rec.purchase_order), ('name', 'ilike', 'WH/%')],
                fields=['name']
            )

            vals = {}
            if not rec.x_picking_in:
                picking_in = next((p for p in related_pickings if 'WH/PICK' in p['name']), None)
                if picking_in:
                    vals['x_picking_in'] = picking_in['name']
            if not rec.x_delivery_out:
                picking_out = next((p for p in related_pickings if 'WH/OUT' in p['name']), None)
                if picking_out:
                    vals['x_delivery_out'] = picking_out['name']

            if vals:
                rec.write(vals)
