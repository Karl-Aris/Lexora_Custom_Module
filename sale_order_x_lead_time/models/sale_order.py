
from odoo import models, fields, api
from datetime import datetime

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
            if order.date_order and order.picking_ids.filtered(lambda p: p.date_done):
                latest_done = max(order.picking_ids.filtered(lambda p: p.date_done).mapped('date_done'))
                if latest_done and order.date_order:
                    delta = latest_done.date() - order.date_order.date()
                    order.x_lead_time = delta.days
                else:
                    order.x_lead_time = 0
            else:
                order.x_lead_time = 0

    @api.model
    def _update_existing_lead_times(self):
        orders = self.search([])
        orders._compute_x_lead_time()
