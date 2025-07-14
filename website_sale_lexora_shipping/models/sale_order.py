from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string="PO #")

    _sql_constraints = [
        ('unique_purchase_order', 'unique(purchase_order)', 'PO # must be unique.')
    ]
