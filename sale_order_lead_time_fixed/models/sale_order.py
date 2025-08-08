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

    @api.depends('lead_time')
    def _compute_expected_delivery_date(self):
        # Determine which confirmation field exists
        confirmation_field = None
        sample_order = self[:1]
        if sample_order:
            fields_available = self.env['sale.order'].fields_get()
            if 'confirmation_date_utc' in fields_available:
                confirmation_field = 'confirmation_date_utc'
            elif 'confirmation_date' in fields_available:
                confirmation_field = 'confirmation_date'
            else:
                confirmation_field = None  # fallback to date_order

        for order in self:
            date_to_use = False
            if confirmation_field:
                dt = getattr(order, confirmation_field)
                if dt:
                    # convert datetime to local date
                    date_to_use = fields.Datetime.context_timestamp(order, dt).date()
            if not date_to_use and order.date_order:
                # fallback: use date_order datetime converted to date
                date_to_use = fields.Datetime.context_timestamp(order, order.date_order).date()

            if date_to_use:
                order.expected_delivery_date = date_to_use + timedelta(days=order.lead_time)
            else:
                order.expected_delivery_date = False
