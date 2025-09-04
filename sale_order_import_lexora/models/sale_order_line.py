from odoo import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    default_code = fields.Char(related="product_id.default_code")
