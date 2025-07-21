from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send_prepare_values(self, mail_values=None):
        values = super()._send_prepare_values(mail_values)
        if self.email_bcc:
            values['bcc'] = self.email_bcc.split(',') if isinstance(self.email_bcc, str) else self.email_bcc
        return values
