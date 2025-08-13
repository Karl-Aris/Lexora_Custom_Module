from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Integer(
        string='Lead Time (days)',
        compute='_compute_x_lead_time',
        store=True,
    )

    @api.depends('picking_ids.date_done', 'confirmation_date')
    def _compute_x_lead_time(self):
        for order in self:
            # Use the confirmation date of the sale order as the start
            start_date = order.confirmation_date.date() if order.confirmation_date else None
            # Get all done picking dates
            done_dates = order.picking_ids.filtered(lambda p: p.date_done).mapped('date_done')
            if start_date and done_dates:
                # Take the earliest done date
                end_date = min(done_dates).date() if isinstance(min(done_dates), fields.Datetime) else min(done_dates)
                order.x_lead_time = (end_date - start_date).days
            else:
                order.x_lead_time = 0
