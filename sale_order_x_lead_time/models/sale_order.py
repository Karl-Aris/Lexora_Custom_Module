from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('date_order', 'picking_ids.date_done')
    def _compute_x_lead_time(self):
        for order in self:
            if order.date_order and order.picking_ids:
                done_pickings = order.picking_ids.filtered(lambda p: p.date_done)
                if done_pickings:
                    latest_date_done = max(done_pickings.mapped('date_done'))
                    delta = latest_date_done.date() - order.date_order.date()
                    order.x_lead_time = delta.days
                else:
                    order.x_lead_time = 0
            else:
                order.x_lead_time = 0

    x_lead_time = fields.Integer(
        string='Lead Time (days)',
        compute='_compute_x_lead_time',
        store=True
    )
