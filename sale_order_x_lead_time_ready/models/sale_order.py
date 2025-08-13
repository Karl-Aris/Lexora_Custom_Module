from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Integer(
        string='Lead Time (days)',
        compute='_compute_x_lead_time',
        store=True,
    )

    @api.depends('date_order', 'picking_ids.date_done')
    def _compute_x_lead_time(self):
        for order in self:
            if not order.date_order:
                order.x_lead_time = 0
                continue

            # Get all completed pickings linked to this sale order
            done_pickings = order.picking_ids.filtered(lambda p: p.state == 'done' and p.date_done)
            if not done_pickings:
                order.x_lead_time = 0
                continue

            # Take the latest date_done
            last_done_date = max(done_pickings.mapped('date_done'))

            # Compute difference in days
            order.x_lead_time = (last_done_date.date() - order.date_order.date()).days
