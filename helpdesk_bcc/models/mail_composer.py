from odoo import models, fields

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    bcc = fields.Char('BCC')

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)
        for res_id in res_ids:
            if res_id in mail_values and self.bcc:
                mail_values[res_id]['email_bcc'] = self.bcc
        return mail_values
