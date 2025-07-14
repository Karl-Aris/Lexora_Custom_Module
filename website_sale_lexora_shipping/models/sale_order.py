from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string="PO #", copy=False)
    order_customer = fields.Char(string="Order Customer")
    order_address = fields.Char(string="Order Address")
    order_phone = fields.Char(string="Order Phone")
