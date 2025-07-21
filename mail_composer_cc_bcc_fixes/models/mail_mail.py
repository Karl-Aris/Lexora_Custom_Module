from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send_prepare_values(self, mail_values=None):
        values = super()._send_prepare_values(mail_values)
        if self.email_bcc:
            values['bcc'] = [email.strip() for email in self.email_bcc.split(',') if email.strip()]
        return values
