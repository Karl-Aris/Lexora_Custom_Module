from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('not_delivered', 'Not Delivered'),
        ('delivered', 'Delivered'),
        ('exception', 'Exception'),
    ], string='Delivery Status', tracking=True)

    etd = fields.Date(string='Estimated Time of Delivery (ETD)', tracking=True)
    follow_up_required = fields.Boolean(string='Follow-Up Required', tracking=True)
    actual_delivery_date = fields.Date(string='Actual Delivery Date', tracking=True)

    contacted = fields.Selection([
        ('received_good', 'Received Good'),
        ('received_damaged', 'Received Damaged'),
        ('other', 'Other'),
    ], string='Contacted', tracking=True)

    contact_notes = fields.Text(string='Contact Notes')
