# sale.order extension model
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string="PO #", copy=False)  # Do NOT add required=True here
