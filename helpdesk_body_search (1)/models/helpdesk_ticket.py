from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    body_index = fields.Text(
        string="Ticket Body Index",
        compute="_compute_body_index",
        store=True,
        index=True
    )

    @api.depends('message_ids.body')
    def _compute_body_index(self):
        for ticket in self:
            ticket.body_index = "\n".join(
                m.body or '' for m in ticket.message_ids if m.body
            )