from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'helpdesk_ticket_bcc_rel',
        'ticket_id', 'partner_id',
        string='BCC Recipients')

    def action_send_bcc_email(self):
        for ticket in self:
            bcc_emails = [p.email for p in ticket.bcc_partner_ids if p.email]
            if bcc_emails:
                self.env['mail.mail'].create({
                    'subject': f"[Ticket {ticket.id}] {ticket.name}",
                    'body_html': ticket.description or 'No content',
                    'email_to': '',
                    'email_bcc': ','.join(bcc_emails),
                    'auto_delete': True,
                    'model': self._name,
                    'res_id': ticket.id,
                }).send()
