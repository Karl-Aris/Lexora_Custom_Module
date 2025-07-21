from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.email_bcc:
                # inject BCC directly into email_values
                email_values = {'email_bcc': mail.email_bcc}
                mail.write(email_values)
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
