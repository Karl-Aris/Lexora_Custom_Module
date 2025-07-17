from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        'res.partner', string='BCC Partners', help="Partners to BCC on outgoing messages"
    )

    def message_post(self, **kwargs):
        bcc_partners = self.bcc_partner_ids
        if bcc_partners:
            email_values = kwargs.get('email_values', {})
            bcc_emails = list(set(bcc_partners.mapped('email')))
            email_values.update({
                'bcc_email': ','.join(filter(None, bcc_emails)),
            })
            kwargs['email_values'] = email_values
        return super().message_post(**kwargs)
