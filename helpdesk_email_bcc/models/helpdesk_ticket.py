from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'helpdesk_ticket_bcc_rel',
        'ticket_id', 'partner_id',
        string='BCC Recipients',
        help="Partners to BCC when sending ticket updates."
    )

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
