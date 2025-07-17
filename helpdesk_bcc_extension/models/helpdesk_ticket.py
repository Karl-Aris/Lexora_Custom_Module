from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        # Remove unsupported key
        bcc_partners = kwargs.pop('bcc_partner_ids', False)

        # Call original message_post
        message = super().message_post(**kwargs)

        # Do your custom BCC logic
        if bcc_partners:
            bcc_emails = self.env['res.partner'].browse(bcc_partners).mapped('email')
            if bcc_emails:
                self.env['mail.mail'].create({
                    'subject': kwargs.get('subject', f'Re: {self.display_name}'),
                    'body_html': kwargs.get('body', ''),
                    'email_from': self.env.user.email_formatted,
                    'email_bcc': ','.join(bcc_emails),
                    'auto_delete': True,
                }).send()

        return message
