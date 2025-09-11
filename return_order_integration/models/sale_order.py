from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    return_order_ids = fields.One2many("return.order", "sale_order_id", string="Return Orders")
