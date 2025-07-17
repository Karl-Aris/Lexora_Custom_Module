from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many('res.partner', string='BCC Recipients')

    def message_post(self, **kwargs):
        if self.bcc_partner_ids:
            bcc_emails = ','.join(self.bcc_partner_ids.mapped('email'))
            kwargs.setdefault('email_bcc', bcc_emails)

        return super().message_post(**kwargs)

    def action_send_bcc_email(self):
        for ticket in self:
            bcc_emails = ticket.bcc_partner_ids.mapped('email')
            if not bcc_emails:
                continue
            self.env['mail.mail'].create({
                'subject': f"Ticket #{ticket.id}: {ticket.name}",
                'body_html': ticket.description or 'No content.',
                'email_to': '',  # no visible to
                'email_bcc': ','.join(bcc_emails),
            }).send()
