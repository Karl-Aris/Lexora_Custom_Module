from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        """Inject BCC note into the email body early during composition."""
        mail_values = super().get_mail_values(res_ids)

        # Get all BCC email addresses (normalized)
        bcc_partners = self.recipient_bcc_ids
        bcc_emails = set(p.email.lower() for p in bcc_partners if p.email)

        for res_id in res_ids:
            values = mail_values.get(res_id)
            if not values:
                continue

            # If the current recipient is in BCC, modify the body
            email_to_list = values.get("email_to", "").lower().split(",")
            if any(email.strip() in bcc_emails for email in email_to_list):
                # Add BCC note to body
                if "body" in values and values["body"]:
                    values["body"] = (
                        "<p style='color:gray; font-size:small;'>"
                        "🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply to all.</p>"
                        + values["body"]
                    )

        return mail_values
