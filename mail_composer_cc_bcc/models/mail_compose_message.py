from odoo import models, _
from odoo.exceptions import UserError
import copy
import logging

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

        # Prepare standard email for To + Cc recipients
        to_emails = ','.join(p.email for p in self.recipient_ids if p.email)
        cc_emails = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)

        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = to_emails
        standard_mail_values["email_cc"] = cc_emails
        standard_mail_values["email_bcc"] = ''  # Explicitly remove Bcc
        mail_values_list.append(standard_mail_values)

        # Prepare Bcc emails separately
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Insert visible headers as note in the email body
            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
              <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
              <strong>To:</strong> {to_emails}<br/>
              <strong>Cc:</strong> {cc_emails}<br/>
              <em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em>
            </p>
            """

            original_body = bcc_mail_values.get('body', '')
            bcc_mail_values["body"] = header_note + original_body
            bcc_mail_values["body_html"] = bcc_mail_values["body"]

            # Keep the visible To and Cc headers
            bcc_mail_values["email_to"] = to_emails
            bcc_mail_values["email_cc"] = cc_emails
            bcc_mail_values["email_bcc"] = ''  # Hide Bcc field

            # Ensure only the Bcc recipient receives this
            bcc_mail_values["recipient_ids"] = [(6, 0, [partner.id])]

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
