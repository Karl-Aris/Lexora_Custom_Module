from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_sale_order_id = fields.Many2one('sale.order', string='Related Sale Order')
