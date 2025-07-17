from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        bcc_partners = kwargs.pop('bcc_partner_ids', False)

        # Post the normal message first
        message = super().message_post(**kwargs)

        if bcc_partners:
            bcc_emails = self.env['res.partner'].browse(bcc_partners).mapped('email')
            if bcc_emails:
                mail_values = {
                    'subject': kwargs.get('subject', f'Re: {self.display_name}'),
                    'body_html': kwargs.get('body', ''),
                    'email_from': self.env.user.email_formatted,
                    'email_bcc': ','.join(bcc_emails),
                    'auto_delete': True,
                }
                self.env['mail.mail'].create(mail_values).send()

        return message
