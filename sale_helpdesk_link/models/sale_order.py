from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_x_matched_sale_order_ids_helpdesk_ticket_count = fields.Integer(
        string='Tickets Count',
        compute='_compute_helpdesk_ticket_count'
    )

    def _compute_helpdesk_ticket_count(self):
        for record in self:
            record.x_x_matched_sale_order_ids_helpdesk_ticket_count = self.env['helpdesk.ticket'].search_count([
                ('x_matched_sale_order_ids', '=', record.id)
            ])
