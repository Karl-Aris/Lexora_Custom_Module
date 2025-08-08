from datetime import timedelta
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_time = fields.Float(string='Lead Time (days)', compute='_compute_lead_time', store=True)
    expected_delivery_date = fields.Date(string='Expected Delivery Date', compute='_compute_expected_delivery_date', store=True)

    @api.depends('order_line.product_id.product_tmpl_id.sale_delay')
    def _compute_lead_time(self):
        for order in self:
            if order.order_line:
                delays = order.order_line.mapped('product_id.product_tmpl_id.sale_delay')
                order.lead_time = max(delays) if delays else 0.0
            else:
                order.lead_time = 0.0

    @api.depends('date_order', 'lead_time')
    def _compute_expected_delivery_date(self):
        for order in self:
            if order.date_order and order.lead_time:
                date_to_use = order.date_order.date() if isinstance(order.date_order, fields.Datetime) else order.date_order
                order.expected_delivery_date = date_to_use + timedelta(days=order.lead_time)
            else:
                order.expected_delivery_date = False
