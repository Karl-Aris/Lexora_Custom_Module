from odoo import models
from odoo.tools import html2plaintext
import copy

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()
        mail_values = self._get_mail_values([self.id])[self.id]
        mail_values_list = []

        # Prepare standard mail with To and Cc
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(
            p.email for p in self.recipient_ids if p.email
        )
        standard_mail_values["email_cc"] = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email
        )
        standard_mail_values["email_bcc"] = ''

        mail_values_list.append(standard_mail_values)

        # Prepare individual emails for each BCC recipient
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Add BCC disclaimer to the top of body
            note = "<p><i>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</i></p>"
            if 'body' in bcc_mail_values and note not in bcc_mail_values['body']:
                bcc_mail_values["body"] = note + bcc_mail_values["body"]
                bcc_mail_values["body_html"] = bcc_mail_values["body"]

            # Clear TO, CC, BCC and set only the BCC recipient in TO field
            bcc_mail_values["email_to"] = partner.email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
