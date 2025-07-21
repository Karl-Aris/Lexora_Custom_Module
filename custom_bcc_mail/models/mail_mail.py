from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.state not in ('outgoing', 'exception'):
                continue

            # Prepare base email payload
            email_values = {
                'email_to': mail.email_to,
                'email_cc': mail.email_cc,
                'subject': mail.subject,
                'body': mail.body,
                'email_bcc': mail.email_bcc,  # inject BCC directly
                'reply_to': mail.reply_to,
                'headers': mail.headers,
                'attachments': [(a['filename'], a['content']) for a in mail.attachment_ids._get_mail_attachments()],
            }

            # Send using preferred mail server
            mail.mail_server_id.send_email(
                message=mail,
                email_values=email_values,
                smtp_server=mail.mail_server_id,
                auto_commit=auto_commit,
                raise_exception=raise_exception
            )

            mail.state = 'sent'
        return True
