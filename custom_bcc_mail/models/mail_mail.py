from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.state not in ('outgoing', 'exception'):
                continue

            attachments = []
            for attach in mail.attachment_ids:
                attachments.append((attach.name, attach.raw or attach.datas))

            email_values = {
                'email_to': mail.email_to,
                'email_cc': mail.email_cc,
                'email_bcc': mail.email_bcc,  # BCC injection here
                'subject': mail.subject,
                'body': mail.body,
                'reply_to': mail.reply_to,
                'headers': mail.headers or {},
                'attachments': attachments,
            }

            mail.mail_server_id.send_email(
                message=mail,
                email_values=email_values,
                smtp_server=mail.mail_server_id,
                auto_commit=auto_commit,
                raise_exception=raise_exception
            )

            mail.state = 'sent'

        return True
