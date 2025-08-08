
from odoo import models, fields, api
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_time = fields.Float(
        string='Lead Time (days)',
        compute='_compute_lead_time',
        store=True,
    )

    expected_delivery_date = fields.Date(
        string='Expected Delivery Date',
        compute='_compute_expected_delivery_date',
        store=True,
    )

    @api.depends('order_line.delay')
    def _compute_lead_time(self):
        for order in self:
            if order.order_line:
                order.lead_time = max(order.order_line.mapped('delay'))
            else:
                order.lead_time = 0.0

    @api.depends('confirmation_date', 'lead_time')
    def _compute_expected_delivery_date(self):
        for order in self:
            if order.confirmation_date:
                order.expected_delivery_date = fields.Date.from_string(order.confirmation_date) + timedelta(days=order.lead_time)
            else:
                order.expected_delivery_date = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delay = fields.Float(
        'Delivery Lead Time',
        help="Number of days between order confirmation and delivery",
        default=0.0,
    )

    @api.onchange('product_id')
    def _onchange_product_id_set_delay(self):
        for line in self:
            if line.product_id:
                line.delay = line.product_id.sale_delay
            else:
                line.delay = 0.0
