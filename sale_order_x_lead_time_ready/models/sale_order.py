from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_lead_time = fields.Integer(
        string='Lead Time (days)',
        compute='_compute_x_lead_time',
        store=True,
    )

    @api.depends('commitment_date', 'effective_date')
    def _compute_x_lead_time(self):
        for order in self:
            d1 = order.commitment_date
            d2 = order.effective_date
            if not d1 or not d2:
                order.x_lead_time = 0
                continue
            try:
                d1_date = fields.Date.to_date(d1) if not isinstance(d1, date) else d1
            except Exception:
                try:
                    d1_date = d1.date()
                except Exception:
                    d1_date = None
            try:
                d2_date = fields.Date.to_date(d2) if not isinstance(d2, date) else d2
            except Exception:
                try:
                    d2_date = d2.date()
                except Exception:
                    d2_date = None
            if not d1_date or not d2_date:
                order.x_lead_time = 0
                continue
            delta = (d1_date - d2_date).days
            order.x_lead_time = abs(delta)
