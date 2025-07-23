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
        try:
            mail_values_dict = self._get_mail_values([self.id])
            mail_values = mail_values_dict.get(self.id)
        except Exception as e:
            _logger.error("Error getting mail values: %s", e)
            raise UserError(_("An error occurred while preparing the email. Please try again."))

        if not mail_values:
            raise UserError(_("Could not generate mail values for this message."))

        mail_values_list = []

        # Prepare standard email with To and Cc
        email_to = ','.join(p.email for p in self.recipient_ids if p.email)
        email_cc = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)

        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = email_to
        standard_mail_values["email_cc"] = email_cc
        standard_mail_values["email_bcc"] = ''  # don't send all BCCs in one

        mail_values_list.append(standard_mail_values)

        # Send BCCs as individual emails (with visible headers in body)
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Insert visible headers for BCC recipient
            header_note = f"""
            <div style="background-color:#f5f5f5; padding:10px; font-family:Arial, sans-serif; font-size:13px;">
                <p>
                    <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
                    <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
                    <strong>To:</strong> {email_to or '(None)'}<br/>
                    <strong>Cc:</strong> {email_cc or '(None)'}<br/>
                    <strong>Bcc:</strong> {partner.email}<br/>
                    <strong>Subject:</strong> {self.subject or '(No Subject)'}<br/>
                </p>
                <p style="color:gray; font-style:italic;">
                    🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.
                </p>
            </div><br/>
            """

            original_body = bcc_mail_values.get('body', '')
            bcc_mail_values["body"] = header_note + original_body
            bcc_mail_values["body_html"] = bcc_mail_values["body"]

            bcc_mail_values["email_to"] = partner.email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
