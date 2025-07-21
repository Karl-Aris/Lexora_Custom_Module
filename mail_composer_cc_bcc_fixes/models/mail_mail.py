from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.email_bcc:
                # This ensures BCC is passed to the mail gateway
                mail.email_bcc = ', '.join(
                    email.strip() for email in mail.email_bcc.split(',') if email.strip()
                )
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
