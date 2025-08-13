
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_number = fields.Char(string='Tracking Number')
    estimated_delivery_date = fields.Date(string='Estimated Delivery Date')
