from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import copy
import logging

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()

        # Get standard mail values
        mail_values_dict = self._get_mail_values([self.id])
        mail_values = mail_values_dict.get(self.id)
        if not mail_values:
            raise UserError(_("Could not generate mail values for this message."))

        mail_values_list = []

        # Prepare To and Cc for header reuse
        email_to_header = ','.join(
            p.email for p in self.recipient_ids if p.email
        )
        email_cc_header = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email
        )

        # Send standard message (To + Cc only)
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = email_to_header
        standard_mail_values["email_cc"] = email_cc_header
        standard_mail_values["email_bcc"] = ''  # Remove BCC
        mail_values_list.append(standard_mail_values)

        # Send each BCC as an individual email (with To and Cc preserved)
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Visible headers in email body
            header_note_html = f"""
            <div style="font-family:Arial, sans-serif; font-size:13px; color:#444;">
              <p><strong>From:</strong> {tools.formataddr((self.env.user.name, self.email_from or 'no-reply@example.com'))}</p>
              <p><strong>Reply-To:</strong> {tools.formataddr(('Lexora', self.reply_to or self.email_from or 'no-reply@example.com'))}</p>
              <p><strong>To:</strong> {email_to_header}</p>
              <p><strong>Cc:</strong> {email_cc_header}</p>
              <p><em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em></p>
              <hr style="border:none;border-top:1px solid #ccc;" />
            </div>
            """

            header_note_plain = f"""From: {self.env.user.name} <{self.email_from or 'no-reply@example.com'}>
Reply-To: Lexora <{self.reply_to or self.email_from or 'no-reply@example.com'}>
To: {email_to_header}
Cc: {email_cc_header}
(Bcc: {partner.email})
🔒 You received this email as a BCC. Please do not reply all.

"""

            original_body = bcc_mail_values.get('body', '')
            bcc_mail_values["body"] = header_note_plain + html2plaintext(original_body or "")
            bcc_mail_values["body_html"] = header_note_html + (original_body or "")

            # Preserve headers for To/Cc but send only to this BCC
            bcc_mail_values["email_to"] = email_to_header
            bcc_mail_values["email_cc"] = email_cc_header
            bcc_mail_values["email_bcc"] = ''

            # Limit delivery to the BCC only
            bcc_mail_values["recipient_ids"] = [(6, 0, [partner.id])]

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
