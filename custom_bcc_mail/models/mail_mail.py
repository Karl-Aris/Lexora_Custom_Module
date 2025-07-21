from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.state not in ('outgoing', 'exception'):
                continue

            email_values = mail._send_prepare_values()

            # Inject BCC directly into outgoing payload
            if mail.email_bcc:
                email_values['email_bcc'] = mail.email_bcc

            # Use Odoo mail server
            mail.mail_server_id.send_email(
                message=mail,
                email_values=email_values,
                smtp_server=mail.mail_server_id,
                auto_commit=auto_commit,
                raise_exception=raise_exception
            )

            mail.state = 'sent'
        return True
