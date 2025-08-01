from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_date = fields.Date(
        string='Sale Order Date',
        compute='_compute_sale_order_date',
        store=True
    )

    @api.depends('invoice_origin')
    def _compute_sale_order_date(self):
        for move in self:
            sale_order = self.env['sale.order'].search([
                ('name', '=', move.invoice_origin)
            ], limit=1)
            move.sale_order_date = sale_order.date_order if sale_order else False
