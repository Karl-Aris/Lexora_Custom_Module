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
        if 'email_layout_xmlid' in kwargs or 'template_id' in kwargs:
            # Extract email addresses from bcc_partner_ids
            bcc_emails = [partner.email for partner in self.bcc_partner_ids if partner.email]

            # Inject BCC in email context if not already passed
            ctx = kwargs.get('mail_post_autofollow', True)
            if bcc_emails:
                # Force context and override email values
                ctx = dict(self.env.context, bcc=bcc_emails)
                self = self.with_context(ctx)

        return super(HelpdeskTicket, self).message_post(**kwargs)
