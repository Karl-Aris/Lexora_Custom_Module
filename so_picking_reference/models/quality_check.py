from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_out_id = fields.Char(
        string="Delivery Quality Check ID",
        readonly=True
    )

    x_return_id = fields.Char(
        string="Return Quality Check ID",
        readonly=True
    )

 
