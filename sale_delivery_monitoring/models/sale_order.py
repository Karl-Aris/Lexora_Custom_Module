from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_number = fields.Char(string="Tracking Number")
    estimated_delivery_date = fields.Date(string="Estimated Delivery Date")
    delivery_status = fields.Selection([
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('not_delivered_on_edd', 'Not Delivered on EDD'),
        ('exception', 'Exception'),
    ], string="Delivery Status", default='shipped')
    follow_up_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ], string="Follow-up Status", default='pending')

    @api.model
    def cron_check_delivery_status(self):
        """Check delivery status daily and auto-categorize."""
        today = date.today()
        orders = self.search([
            ('delivery_status', '=', 'shipped'),
            ('estimated_delivery_date', '<', today)
        ])
        for order in orders:
            order.delivery_status = 'not_delivered_on_edd'
