from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('date_order', 'commitment_date')
    def _compute_x_lead_time(self):
        for order in self:
            if order.date_order and order.commitment_date:
                # Ensure date types
                date_order = fields.Date.to_date(order.date_order)
                commitment_date = fields.Date.to_date(order.commitment_date)
                # Compute difference in days
                order.x_lead_time = (commitment_date - date_order).days
            else:
                order.x_lead_time = 0

    # Attach the compute method to your existing field
    x_lead_time = fields.Integer(
        string="Lead Time (days)",
        compute="_compute_x_lead_time",
        store=True
    )
