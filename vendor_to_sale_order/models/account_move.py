from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', string="Related Sale Order")
    x_po_vb_id = fields.Char(string="PO# from Sale Order")
