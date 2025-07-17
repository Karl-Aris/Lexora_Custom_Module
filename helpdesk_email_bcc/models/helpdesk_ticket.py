from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many('res.partner', string='BCC Recipients')

    def action_send_bcc_email(self):
        Mail = self.env['mail.mail']
        for ticket in self:
            bcc_emails = ticket.bcc_partner_ids.filtered(lambda p: p.email).mapped('email')
            if not bcc_emails:
                continue

            Mail.create({
                'subject': f"[Ticket #{ticket.id}] {ticket.name}",
                'body_html': ticket.description or "<p>No content.</p>",
                'email_from': self.env.user.email or self.env.company.email,
                'email_to': '',  # hidden TO
                'email_bcc': ','.join(bcc_emails),
                'model': 'helpdesk.ticket',
                'res_id': ticket.id,
            }).send()
