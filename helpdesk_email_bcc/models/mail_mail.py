# file: models/mail_mail.py

from odoo import models, fields

class MailMail(models.Model):
    _inherit = 'mail.mail'

    email_bcc = fields.Char(string='BCC Emails')

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.email_bcc:
                mail.bcc = mail.email_bcc
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
