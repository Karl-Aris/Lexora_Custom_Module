from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(
        string="Tracking Number",
        copy=False,
        help="Tracking number received from the carrier webhook."
    )
