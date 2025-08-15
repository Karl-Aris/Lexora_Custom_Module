from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ], string="Delivery Status")

    etd = fields.Date(string="ETD")
    follow_up_required = fields.Boolean(string="Follow Up Required")
    actual_delivery_date = fields.Date(string="Actual Delivery Date")
    contacted = fields.Boolean(string="Contacted")
    contact_notes = fields.Text(string="Contact Notes")