from odoo import models
import html

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_mail_values(self, res_ids):
        mail_values = super()._get_mail_values(res_ids)

        for res_id in res_ids:
            values = mail_values[res_id]
            bcc_recipients = self.recipient_bcc_ids

            if bcc_recipients:
                # BCC-specific note
                bcc_note = (
                    "<p style='color:gray; font-style:italic;'>"
                    "🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all.</p>"
                )

                # Insert note only for BCC recipients
                values["body_html"] = bcc_note + values.get("body_html", "")
                values["body"] = bcc_note + values.get("body", "")
                mail_values[res_id] = values

        return mail_values
