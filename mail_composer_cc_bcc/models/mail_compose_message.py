from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        return super().get_mail_values(res_ids)
