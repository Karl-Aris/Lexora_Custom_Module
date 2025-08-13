from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Integer(
        string='Lead Time (days)',
        compute='_compute_x_lead_time',
        store=True,
    )

    @api.depends('date_order')
    def _compute_x_lead_time(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if not order.date_order:
                order.x_lead_time = 0
                continue

            pickings = StockPicking.search([
                ('sale_id', '=', order.id),
                ('state', '=', 'done')
            ])
            if not pickings:
                order.x_lead_time = 0
                continue

            last_done = max(pickings.mapped('date_done'))
            if last_done:
                delta_days = (last_done - order.date_order).days
                order.x_lead_time = delta_days
            else:
                order.x_lead_time = 0
