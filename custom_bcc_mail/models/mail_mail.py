from odoo import models
from odoo.tools.mail import is_mail_server

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        MailDelivery = self.env['mail.mail']
        for mail in self:
            if mail.state not in ('outgoing', 'exception'):
                continue

            email_dict = mail._send_prepare_values()
            # Properly inject BCC
            if mail.email_bcc:
                email_dict['email_bcc'] = mail.email_bcc

            # Use internal delivery method (SMTP/Sendgrid/etc.)
            smtp_server = mail.mail_server_id or self.env['ir.mail_server'].sudo().search([], limit=1)
            smtp_server.send_email(
                message=mail,
                smtp_server=smtp_server,
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                email_values=email_dict
            )
            mail.state = 'sent'
        return True
