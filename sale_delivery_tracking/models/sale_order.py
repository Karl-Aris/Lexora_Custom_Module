from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ], string="Delivery Status")

    x_etd = fields.Date(string="ETD")
    x_follow_up_required = fields.Boolean(string="Follow Up Required")
    x_actual_delivery_date = fields.Date(string="Actual Delivery Date")
    x_contacted = fields.Boolean(string="Contacted")
    x_contact_notes = fields.Text(string="Contact Notes")
