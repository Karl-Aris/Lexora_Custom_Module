from datetime import timedelta
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_time = fields.Float(string='Lead Time (days)', compute='_compute_lead_time', store=True)
    expected_delivery_date = fields.Date(string='Expected Delivery Date', compute='_compute_expected_delivery_date', store=True)

    @api.depends('order_line.product_id.product_tmpl_id.sale_delay')
    def _compute_lead_time(self):
        for order in self:
            delays = []
            for line in order.order_line:
                tmpl = line.product_id.product_tmpl_id
                if tmpl:
                    if 'sale_delay' in tmpl._fields:
                        delays.append(tmpl.sale_delay or 0)
                    else:
                        _logger = self.env['ir.logging']
                        _logger.create({
                            'name': 'Lead Time Compute',
                            'type': 'server',
                            'dbname': self.env.cr.dbname,
                            'level': 'warning',
                            'message': _('Product template missing sale_delay field: %s') % tmpl.id,
                            'path': 'sale.order',
                            'func': '_compute_lead_time',
                            'line': 'custom',
                        })
            order.lead_time = max(delays) if delays else 0.0

    @api.depends('date_order', 'lead_time')
    def _compute_expected_delivery_date(self):
        for order in self:
            if order.date_order and order.lead_time:
                date_to_use = order.date_order.date() if isinstance(order.date_order, fields.Datetime) else order.date_order
                order.expected_delivery_date = date_to_use + timedelta(days=order.lead_time)
            else:
                order.expected_delivery_date = False
