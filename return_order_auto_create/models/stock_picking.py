from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _is_return_picking_name(self, name):
        if not name:
            return False
        return 'WH/INT/RETURN' in (name.upper())

    @api.model_create_multi
    def create(self, vals_list):
        records = super(StockPicking, self).create(vals_list)
        ReturnOrder = self.env['return.order']
        for rec in records:
            try:
                is_return = self._is_return_picking_name(rec.name)
                if is_return:
                    # avoid duplicates
                    existing = ReturnOrder.sudo().search([('picking_id', '=', rec.id)], limit=1)
                    if not existing:
                        vals = {
                            'name': rec.name or False,
                            'sale_order_id': rec.sale_id.id if hasattr(rec, 'sale_id') and rec.sale_id else False,
                            'partner_id': rec.partner_id.id if rec.partner_id else False,
                            'picking_id': rec.id,
                            'state': 'initiated',
                        }
                        # attempt to include Studio field x_location if destination exists
                        if hasattr(rec, 'location_dest_id') and rec.location_dest_id:
                            vals['x_location'] = rec.location_dest_id.display_name
                        ReturnOrder.sudo().create(vals)
            except Exception:
                # fail silently here to avoid breaking picking creation; errors logged server-side
                self.env.cr.rollback()
        return records

    def action_done(self):
        res = super(StockPicking, self).action_done()
        ReturnOrder = self.env['return.order']
        for rec in self:
            if self._is_return_picking_name(rec.name):
                ro = ReturnOrder.sudo().search([('picking_id', '=', rec.id)], limit=1)
                if ro:
                    ro.sudo().write({'state': 'returned'})
        return res
