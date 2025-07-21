from odoo import models, fields

class MailMail(models.Model):
    _inherit = 'mail.mail'

    custom_bcc = fields.Char(string='Custom BCC')

    def _send_prepare_values(self, mail_values=None):
        values = super()._send_prepare_values(mail_values)
        if self.custom_bcc:
            bcc_list = [email.strip() for email in self.custom_bcc.split(',') if email.strip()]
            values['bcc'] = bcc_list
        return values
