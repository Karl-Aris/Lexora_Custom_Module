from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Float(
        string="Lead Time (days)",
        compute="_compute_x_lead_time",
        store=True
    )

    @api.depends('date_order')  # Only depend on date_order
    def _compute_x_lead_time(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if not order.date_order:
                order.x_lead_time = 0
                continue

            # Find all done pickings for this sale order
            pickings = StockPicking.search([
                ('sale_id', '=', order.id),
                ('state', '=', 'done')
            ])
            if pickings:
                last_done = max(pickings.mapped('date_done'))
                order.x_lead_time = (last_done - order.date_order).days
            else:
                order.x_lead_time = 0
