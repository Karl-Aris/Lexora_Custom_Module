from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_date = fields.Date(
        string='Sale Order Date',
        compute='_compute_sale_order_date',
        store=True,
    )

    def _compute_sale_order_date(self):
        for move in self:
            sale_orders = move.invoice_origin and self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
            move.sale_order_date = sale_orders.confirmation_date if sale_orders else False
