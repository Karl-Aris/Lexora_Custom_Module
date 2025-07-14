# in models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string="PO #")
