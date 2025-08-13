from odoo import api, fields, models
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_tracking_number = fields.Char(string='Tracking Number', tracking=True)
    x_edd_date = fields.Date(string='Estimated Delivery Date (EDD)', tracking=True)

    delivery_status = fields.Selection([
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('not_delivered_on_edd', 'Not Delivered on EDD'),
        ('exception', 'Exception'),
    ], string='Delivery Status', default='shipped', tracking=True, index=True)

    follow_up_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')
    ], string='Follow-Up Status', default='pending', tracking=True, index=True)

    x_delivery_note = fields.Text(string='Delivery Note', tracking=True, help='Optional notes for delays/exceptions or call outcomes.')

    # Convenience computed flags for filters (optional)
    is_edd_today_or_earlier = fields.Boolean(string='EDD Today or Earlier', compute='_compute_is_edd_today_or_earlier', search='_search_is_edd_today_or_earlier')

    @api.depends('x_edd_date')
    def _compute_is_edd_today_or_earlier(self):
        today = date.today()
        for order in self:
            order.is_edd_today_or_earlier = bool(order.x_edd_date and order.x_edd_date <= today)

    def _search_is_edd_today_or_earlier(self, operator, value):
        # Support domain [('is_edd_today_or_earlier', '=', True)]
        if operator in ('=', '==') and value:
            return [('x_edd_date', '<=', fields.Date.context_today(self))]
        if operator in ('=', '==') and not value:
            return ['|', ('x_edd_date', '=', False), ('x_edd_date', '>', fields.Date.context_today(self))]
        # Fallback
        return []

    # Hook: when tracking number or EDD is set the first time, default to shipped
    @api.onchange('x_tracking_number', 'x_edd_date')
    def _onchange_shipping_inputs(self):
        for order in self:
            if (order.x_tracking_number or order.x_edd_date) and not order.delivery_status:
                order.delivery_status = 'shipped'

    # Cron entry point: auto categorize by EDD and (optionally) carrier API
    @api.model
    def cron_auto_categorize_delivery_status(self, limit=1000):
        today = fields.Date.context_today(self)
        domain = [
            ('delivery_status', '=', 'shipped'),
            ('x_edd_date', '!=', False),
            ('x_edd_date', '<=', today),
        ]
        orders = self.search(domain, limit=limit)
        # Basic rule: missed EDD → Not Delivered on EDD
        for order in orders:
            # Placeholder for future API integration; currently we set the bucket
            order.delivery_status = 'not_delivered_on_edd'
        if orders:
            self.env.cr.commit()
        return True

    # Public helper methods for manual actions (can be used by buttons if needed)
    def action_mark_delivered(self):
        for order in self:
            order.delivery_status = 'delivered'

    def action_mark_in_transit(self):
        for order in self:
            order.delivery_status = 'in_transit'

    def action_mark_exception(self):
        for order in self:
            order.delivery_status = 'exception'
