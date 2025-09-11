from odoo import models, fields, api
from odoo.tools import safe_eval

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # We won't override create globally, but we'll hook into _action_done and create helper method
    def _create_return_order_if_needed(self):
        """Create a return.order when picking looks like a return (name contains RETURN or picking type is return/internal)."""
        ReturnOrder = self.env['return.order']
        for rec in self:
            # simple heuristic: name contains 'RETURN' or the picking type code is 'internal' and origin includes 'Return'
            name_upper = (rec.name or '').upper()
            is_return_name = 'RETURN' in name_upper or (rec.picking_type_id and rec.picking_type_id.code == 'internal' and 'RETURN' in name_upper)
            if is_return_name:
                # avoid duplicates
                existing = ReturnOrder.search([('picking_id', '=', rec.id)], limit=1)
                if not existing:
                    vals = {
                        'name': rec.origin or rec.name or 'Return/%s' % (rec.id),
                        'sale_order_id': rec.sale_id.id if hasattr(rec, 'sale_id') and rec.sale_id else False,
                        'picking_id': rec.id,
                        'state': 'initiated',
                        'date_shipped': rec.scheduled_date,
                    }
                    ReturnOrder.create(vals)

    def action_done(self):
        res = super(StockPicking, self).action_done()
        # After validation, update related return.order if any
        for rec in self:
            rec._create_return_order_if_needed()
            ro = self.env['return.order'].search([('picking_id', '=', rec.id)], limit=1)
            if ro:
                ro.write({'state': 'returned', 'return_date': fields.Date.context_today(self)})
        return res
