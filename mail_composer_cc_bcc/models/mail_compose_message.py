from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        # Do not inject the BCC notice here — it's handled later in mail.mail
        return super().get_mail_values(res_ids)
