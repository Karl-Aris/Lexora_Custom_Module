from odoo import models, api, tools


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)

        has_bcc = bool(self.bcc_partner_ids)

        for res_id, values in mail_values.items():
            if has_bcc:
                # Force a unique message_id to avoid reuse and threading issues
                values["message_id"] = tools.generate_tracking_message_id()

        return mail_values
