from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('not_delivered', 'Not Delivered'),
        ('delivered', 'Delivered'),
        ('exception', 'Exception'),
    ], string="Delivery Status")

    etd = fields.Date(string="Estimated Time of Delivery (ETD)")

    follow_up_required = fields.Boolean(string="Follow-Up Required")

    actual_delivery_date = fields.Date(string="Actual Delivery Date")

    contacted = fields.Selection([
        ('received_good', 'Received Good'),
        ('received_damaged', 'Received Damaged'),
        ('other', 'Other'),
    ], string="Contacted")

    contact_notes = fields.Text(string="Contact Notes")
