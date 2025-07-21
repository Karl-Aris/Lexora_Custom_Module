from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    custom_bcc = fields.Char(string='BCC (Custom)')

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)
        for res_id in res_ids:
            if self.custom_bcc:
                mail_values[res_id]['email_bcc'] = self.custom_bcc
        return mail_values
