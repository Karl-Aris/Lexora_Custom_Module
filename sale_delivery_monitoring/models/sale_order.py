from odoo import models, fields
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_number = fields.Char("Tracking Number")
    estimated_delivery_date = fields.Date("Estimated Delivery Date")
    delivery_status = fields.Selection([
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('not_delivered_on_edd', 'Not Delivered on EDD'),
    ], string="Delivery Status", default='shipped', tracking=True)

    follow_up_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ], string="Follow-up Status", default='pending', tracking=True)

    def cron_update_delivery_status(self):
        today = date.today()
        orders = self.search([
            ('delivery_status', '=', 'shipped'),
            ('estimated_delivery_date', '!=', False),
            ('estimated_delivery_date', '<=', today)
        ])
        for order in orders:
            order.delivery_status = 'not_delivered_on_edd'
