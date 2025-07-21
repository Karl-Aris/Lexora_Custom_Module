from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_matched_sale_order_ids = fields.Many2many('sale.order', string="Matched Sale Orders")
    x_x_matched_sale_order_ids_helpdesk_ticket_count = fields.Integer(
        string="Matched Sale Orders Count",
        compute="_compute_matched_sale_order_count"
    )

    def _compute_matched_sale_order_count(self):
        for record in self:
            record.x_x_matched_sale_order_ids_helpdesk_ticket_count = len(record.x_matched_sale_order_ids)
