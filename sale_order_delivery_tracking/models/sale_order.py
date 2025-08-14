from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_delivery_status = fields.Selection([
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('not_delivered_edd', 'Not Delivered on EDD'),
        ('exception', 'Exception')
    ], string="Delivery Status", default='shipped')

    # Using built-in Odoo tracking field instead of custom
    carrier_tracking_ref = fields.Char(string="Tracking Number")

    estimated_delivery_date = fields.Date(string="Estimated Delivery Date")
    follow_up_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')
    ], string="Follow-Up Status", default='pending')

    @api.model
    def update_delivery_status_daily(self):
        today = date.today()
        orders = self.search([
            ('x_delivery_status', '=', 'shipped'),
            ('estimated_delivery_date', '<=', today)
        ])
        for order in orders:
            order.x_delivery_status = 'not_delivered_edd'
            message = f"Auto-updated delivery status to 'Not Delivered on EDD' as of {today}."

            # Chatter log
            order.message_post(body=message, subtype_xmlid="mail.mt_note")

            # Notification for salesperson
            if order.user_id:
                order.activity_schedule(
                    activity_type_xmlid="mail.mail_activity_data_todo",
                    summary="Order missed estimated delivery date",
                    note=message,
                    user_id=order.user_id.id
                )
