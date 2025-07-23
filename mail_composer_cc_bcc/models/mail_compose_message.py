from odoo import models, _
from odoo.exceptions import UserError
import copy
import logging

_logger = logging.getLogger(__name__)

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()

        mail_values_dict = self._get_mail_values([self.id])
        mail_values = mail_values_dict.get(self.id)
        if not mail_values:
            raise UserError(_("Could not generate mail values for this message."))

        mail_values_list = []

        # Standard email for To + Cc
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(p.email for p in self.recipient_ids if p.email)
        standard_mail_values["email_cc"] = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)
        standard_mail_values["email_bcc"] = ''  # No Bcc in this message

        mail_values_list.append(standard_mail_values)

        # Individual emails for each Bcc
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_mail_values = copy.deepcopy(mail_values)

            # Embed visible headers for context
            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
              <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
              <strong>To:</strong> {standard_mail_values.get('email_to', '')}<br/>
              <strong>Cc:</strong> {standard_mail_values.get('email_cc', '')}<br/>
              <em>🔒 You received this email as a BCC. Please do not reply all.</em>
            </p>
            """
            original_body = bcc_mail_values.get('body', '') or ''
            bcc_mail_values["body"] = header_note + original_body
            bcc_mail_values["body_html"] = bcc_mail_values["body"]

            # Send only to this BCC partner
            bcc_mail_values["email_to"] = partner.email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
