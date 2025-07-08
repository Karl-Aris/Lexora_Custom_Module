from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if not mail.email_from and mail.mail_server_id:
                from_filter = mail.mail_server_id.from_filter
                if from_filter:
                    if '@' in from_filter:
                        mail.email_from = from_filter
                    elif mail.mail_server_id.smtp_user:
                        mail.email_from = mail.mail_server_id.smtp_user
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
