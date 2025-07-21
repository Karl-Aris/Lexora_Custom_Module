# File: custom_bcc_mail/models/mail_mail.py
from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        IrMailServer = self.env['ir.mail_server']

        for mail in self:
            if mail.state not in ('outgoing', 'exception'):
                continue

            attachments = []
            for attachment in mail.attachment_ids:
                attachments.append((attachment.name, attachment.raw or attachment.datas))

            # Construct email parameters
            email_dict = {
                'subject': mail.subject,
                'body': mail.body,
                'email_from': mail.email_from,
                'email_to': mail.email_to,
                'email_cc': mail.email_cc,
                'email_bcc': mail.email_bcc,  # Inject custom BCC
                'reply_to': mail.reply_to,
                'attachments': attachments,
                'headers': mail.headers or {},
                'message_id': mail.message_id,
            }

            # Send the email
            try:
                IrMailServer.send_email(
                    email_from=mail.email_from,
                    email_to=mail.email_to,
                    subject=mail.subject,
                    body=email_dict['body'],
                    body_alternative=None,
                    email_cc=mail.email_cc,
                    email_bcc=mail.email_bcc,
                    reply_to=mail.reply_to,
                    attachments=attachments,
                    message_id=mail.message_id,
                    mail_server_id=mail.mail_server_id.id,
                    smtp_session=None,
                    smtp_debug=False,
                )
                mail.state = 'sent'
            except Exception as e:
                mail.state = 'exception'
                mail.failure_reason = str(e)

        return True
