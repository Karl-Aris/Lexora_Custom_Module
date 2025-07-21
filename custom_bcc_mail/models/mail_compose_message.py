from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    email_bcc = fields.Char(string='BCC')

    def send_mail(self, auto_commit=False):
        res = super().send_mail(auto_commit=auto_commit)
        for message in self.mail_message_id:
            mails = self.env['mail.mail'].search([('mail_message_id', '=', message.id)])
            for mail in mails:
                if self.email_bcc:
                    mail.email_bcc = self.email_bcc
        return res
