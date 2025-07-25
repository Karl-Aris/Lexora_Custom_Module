from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Related Sale Order',
    )
