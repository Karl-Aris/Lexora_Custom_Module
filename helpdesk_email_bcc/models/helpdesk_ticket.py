# helpdesk_email_bcc/models/helpdesk_ticket.py

from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many('res.partner', string='BCC Recipients')

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        for ticket in self:
            if ticket.bcc_partner_ids:
                bcc_emails = ','.join(ticket.bcc_partner_ids.mapped('email'))
                if bcc_emails:
                    self.env['mail.mail'].create({
                        'subject': f"Ticket #{ticket.id}: {ticket.name}",
                        'body_html': ticket.description or "<p>No content</p>",
                        'email_to': '',  # no TO
                        'bcc': bcc_emails,
                        'model': 'helpdesk.ticket',
                        'res_id': ticket.id,
                    }).send()
        return res
