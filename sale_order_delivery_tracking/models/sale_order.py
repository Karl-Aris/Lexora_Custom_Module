from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Changed Delivery Status selection
    x_delivery_status = fields.Selection([
        ('delivered', 'Delivered'),
        ('not_delivered', 'Not Delivered'),
        ('other', 'Other'),
    ], string="Delivery Status")

    x_etd = fields.Date(string="ETD")
    x_follow_up_required = fields.Boolean(string="Follow Up Required")
    x_actual_delivery_date = fields.Date(string="Actual Delivery Date")

    # Changed Contacted from Boolean to Selection
    x_contacted = fields.Selection([
        ('received_good', 'Received Good'),
        ('received_damaged', 'Received Damaged'),
        ('other', 'Other'),
    ], string="Contacted")

    x_contact_notes = fields.Text(string="Contact Notes")
