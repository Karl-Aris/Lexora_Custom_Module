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

        # Prepare main message (To + Cc)
        email_to = ','.join(p.email for p in self.recipient_ids if p.email)
        email_cc = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email)

        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values.update({
            "email_to": email_to,
            "email_cc": email_cc,
            "email_bcc": "",  # Don't send BCCs here
        })
        mail_values_list.append(standard_mail_values)

        # Prepare separate BCC messages
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_email = partner.email
            bcc_mail_values = copy.deepcopy(mail_values)

            header_note = f"""
            <p style="color:gray; font-size:small;">
              <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
              <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
              <strong>To:</strong> {email_to}<br/>
              <strong>Cc:</strong> {email_cc}<br/>
              <em>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</em>
            </p>
            """

            bcc_mail_values.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": "",  # Omit actual BCC field
                "headers": {"X-Odoo-Bcc": bcc_email},
                "body": header_note + (bcc_mail_values.get("body") or ""),
                "body_html": header_note + (bcc_mail_values.get("body_html") or ""),
                "recipient_ids": [(6, 0, [partner.id])],
            })

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
