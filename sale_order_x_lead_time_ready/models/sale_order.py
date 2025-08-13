from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Float(
        string="Lead Time (days)",
        compute="_compute_x_lead_time",
        store=True
    )

    @api.depends('date_order', 'picking_ids.date_done')
    def _compute_x_lead_time(self):
        for order in self:
            # Get the latest done date from all related pickings
            done_dates = order.picking_ids.filtered(lambda p: p.state == 'done').mapped('date_done')
            if done_dates and order.date_order:
                last_done = max(done_dates)
                order.x_lead_time = (last_done - order.date_order).days
            else:
                order.x_lead_time = 0
