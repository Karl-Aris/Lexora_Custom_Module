from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        # Call the original behavior
        res = super()._action_send_mail(auto_commit=auto_commit)

        # Assign bcc_recipient_ids to the resulting mail.mail records
        mail_mail = self.env["mail.mail"]
        for wizard in self:
            if wizard.bcc_recipient_ids:
                # Get all mail.mail records linked to the message created by this wizard
                mails = mail_mail.search([
                    ("mail_message_id", "=", wizard.mail_message_id.id)
                ])
                for mail in mails:
                    mail.recipient_bcc_ids = [(6, 0, wizard.bcc_recipient_ids.ids)]

        return res
