from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'helpdesk_ticket_bcc_partner_rel',
        'ticket_id',
        'partner_id',
        string='BCC Partners'
    )

    def message_post(self, **kwargs):
        # Get BCC emails
        bcc_emails = [partner.email for partner in self.bcc_partner_ids if partner.email]

        # Inject BCC into email values if message is meant to be emailed
        if kwargs.get('message_type') == 'email':
            email_values = kwargs.get('email_values', {})
            existing_bcc = email_values.get('bcc', '')

            # Combine existing and new BCCs (if any)
            combined_bcc = existing_bcc.split(',') if existing_bcc else []
            combined_bcc += bcc_emails
            # Remove duplicates
            combined_bcc = list(set([email.strip() for email in combined_bcc if email.strip()]))

            # Update email_values with new BCC list
            email_values['bcc'] = ','.join(combined_bcc)
            kwargs['email_values'] = email_values

        return super(HelpdeskTicket, self).message_post(**kwargs)
