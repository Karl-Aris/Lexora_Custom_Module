from odoo import models, fields, api

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

            # Find all done pickings linked to this sale order
            done_pickings = StockPicking.search([
                ('origin', '=', order.name),
                ('state', '=', 'done'),
                ('date_done', '!=', False)
            ])

            if not done_pickings:
                order.x_lead_time = 0
                continue

            # Get the latest date_done
            last_done_date = max(done_pickings.mapped('date_done'))

            order.x_lead_time = (last_done_date.date() - order.date_order.date()).days
