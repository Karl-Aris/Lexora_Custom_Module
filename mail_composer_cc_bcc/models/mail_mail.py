from odoo import models
from odoo.tools import html2plaintext
import copy

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()
        mail_values = self._get_mail_values([self.id])[self.id]
        mail_values_list = []

        # Prepare standard mail (To, Cc)
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(
            p.email for p in self.recipient_ids if p.email)
        standard_mail_values["email_cc"] = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)
        standard_mail_values["email_bcc"] = ''

        mail_values_list.append(standard_mail_values)

        # Handle BCC separately
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Add BCC Notice to Body
            body_plaintext = html2plaintext(bcc_mail_values.get("body", ""))
            note = "<p>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
            if note not in bcc_mail_values["body"]:
                bcc_mail_values["body"] = note + bcc_mail_values["body"]
                bcc_mail_values["body_html"] = bcc_mail_values["body"]

            # Set only the BCC recipient as "To", clear others
            bcc_mail_values["email_to"] = partner.email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
