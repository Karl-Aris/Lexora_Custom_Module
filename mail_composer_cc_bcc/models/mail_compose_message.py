# mail_composer_cc_bcc/models/mail_compose_message.py

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import copy
import logging
import html  # To escape user-provided values safely

_logger = logging.getLogger(__name__)

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()

        # Safely get mail values
        mail_values_dict = self._get_mail_values([self.id])
        mail_values = mail_values_dict.get(self.id)
        if not mail_values:
            raise UserError(_("Could not generate mail values for this message."))

        mail_values_list = []

        # Prepare standard email with To and Cc
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(
            p.email for p in self.recipient_ids if p.email
        )
        standard_mail_values["email_cc"] = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email
        )
        standard_mail_values["email_bcc"] = ''  # No global BCC on standard email

        mail_values_list.append(standard_mail_values)

        # Send BCCs as individual emails with full To and Cc (but Bcc hidden)
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Insert visible email headers in body
            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {html.escape(self.email_from or 'Lexora')}<br/>
              <strong>Reply-To:</strong> {html.escape(self.reply_to or self.email_from or 'Lexora')}<br/>
              <strong>To:</strong> {html.escape(standard_mail_values.get('email_to', ''))}<br/>
              <strong>Cc:</strong> {html.escape(standard_mail_values.get('email_cc', ''))}<br/>
              <em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em>
            </p>
            """

            original_body = bcc_mail_values.get('body', '')
            new_body = header_note + original_body
            bcc_mail_values["body_html"] = new_body
            bcc_mail_values["body"] = new_body

            # Show original To and Cc in headers
            bcc_mail_values["email_to"] = standard_mail_values.get("email_to", "")
            bcc_mail_values["email_cc"] = standard_mail_values.get("email_cc", "")
            bcc_mail_values["email_bcc"] = partner.email  # Only this BCC partner

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
