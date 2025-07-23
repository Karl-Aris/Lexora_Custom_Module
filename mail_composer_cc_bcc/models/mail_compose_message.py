from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)
        for res_id, values in mail_values.items():
            # Add BCC notice only to the BCC-specific message body
            context_partner_id = self.env.context.get('force_bcc_partner_id')
            if context_partner_id and values.get('body'):
                note = (
                    "<p style='color:gray;font-size:small;'>"
                    "🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all.</p>"
                )
                values['body'] = note + values['body']
        return mail_values
