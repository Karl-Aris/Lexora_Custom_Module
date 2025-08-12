from datetime import timedelta
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(string='Delivery Date')
    lead_time = fields.Float(string='Lead Time (days)', compute='_compute_lead_time', store=True)
    expected_delivery_date = fields.Date(string='Expected Delivery Date', compute='_compute_expected_delivery_date', store=True)

    @api.depends('date_order', 'delivery_date')
    def _compute_lead_time(self):
        for order in self:
            if order.date_order and order.delivery_date:
                # ensure date_order is a datetime, convert and localize to user TZ, then get date()
                try:
                    dt = order.date_order
                    if isinstance(dt, str):
                        dt = fields.Datetime.from_string(dt)
                    date_order_local = fields.Datetime.context_timestamp(order, dt).date()
                except Exception:
                    # fallback: if something odd, try to use date_order directly as date
                    try:
                        date_order_local = order.date_order.date()
                    except Exception:
                        date_order_local = None
                if date_order_local:
                    delta = order.delivery_date - date_order_local
                    order.lead_time = delta.days
                else:
                    order.lead_time = 0.0
            else:
                order.lead_time = 0.0

    @api.depends('delivery_date')
    def _compute_expected_delivery_date(self):
        for order in self:
            order.expected_delivery_date = order.delivery_date or False
