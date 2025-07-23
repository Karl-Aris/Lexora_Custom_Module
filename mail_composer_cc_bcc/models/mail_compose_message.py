# mail_composer_cc_bcc/models/mail_compose_message.py

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import copy
import logging
import html  # escape HTML content

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

        # Prepare ONE standard email with To, Cc, and Bcc
        standard_mail_values = copy.deepcopy(mail_values)

        # Actual To, Cc, and Bcc
        to_emails = ','.join(p.email for p in self.recipient_ids if p.email)
        cc_emails = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)
        bcc_emails = ','.join(p.email for p in getattr(self, 'recipient_bcc_ids', []) if p.email)

        standard_mail_values["email_to"] = to_emails
        standard_mail_values["email_cc"] = cc_emails
        standard_mail_values["email_bcc"] = bcc_emails

        # Optional: Add BCC note in body (only visible to BCC recipients, but OK to include)
        if bcc_emails:
            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {html.escape(self.email_from or 'Lexora')}<br/>
              <strong>Reply-To:</strong> {html.escape(self.reply_to or self.email_from or 'Lexora')}<br/>
              <strong>To:</strong> {html.escape(to_emails)}<br/>
              <strong>Cc:</strong> {html.escape(cc_emails)}<br/>
              <strong>Bcc:</strong> {html.escape(bcc_emails)}<br/>
              <em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em>
            </p>
            """
            body = standard_mail_values.get("body", "")
            standard_mail_values["body"] = header_note + body
            standard_mail_values["body_html"] = header_note + body

        mail_values_list.append(standard_mail_values)
        return mail_values_list
