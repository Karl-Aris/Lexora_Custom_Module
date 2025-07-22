from odoo import models
from odoo.tools import html2plaintext
import copy

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()
        mail_values = self._get_mail_values([self.id])[self.id]
        mail_values_list = []

        # Prepare main (To and Cc) message
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(
            p.email for p in self.recipient_ids if p.email
        )
        standard_mail_values["email_cc"] = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email
        )
        standard_mail_values["email_bcc"] = ''

        mail_values_list.append(standard_mail_values)

        # Handle BCC recipients individually
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Build header block to appear in body
            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
              <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
              <strong>To:</strong> {standard_mail_values.get('email_to', '')}<br/>
              <strong>Cc:</strong> {standard_mail_values.get('email_cc', '')}<br/>
              <strong>Bcc:</strong> {partner.email}<br/>
              <em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em>
            </p>
            """

            # Prepend header block to email body
            if 'body' in bcc_mail_values:
                bcc_mail_values["body"] = header_note + bcc_mail_values["body"]
                bcc_mail_values["body_html"] = bcc_mail_values["body"]

            # Only send to BCC recipient
            bcc_mail_values["email_to"] = partner.email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
