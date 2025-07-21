from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_matched_sale_order_ids = fields.Many2many('sale.order', string="Matched Sale Orders")
    x_matched_sale_order_count = fields.Integer(string="Matched SO Count", compute="_compute_matched_sale_order_count")

    def _compute_matched_sale_order_count(self):
        for record in self:
            record.x_matched_sale_order_count = len(record.x_matched_sale_order_ids)

    def action_view_matched_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Matched Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.x_matched_sale_order_ids.ids)],
            'context': {'create': False}
        }
