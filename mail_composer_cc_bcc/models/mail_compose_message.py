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

        # Get TO and CC as string
        to_emails = [p.email for p in self.recipient_ids if p.email]
        cc_emails = [p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email]

        to_display = ', '.join(to_emails)
        cc_display = ', '.join(cc_emails)

        # 1. Standard email (To + Cc)
        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = to_display
        standard_mail_values["email_cc"] = cc_display
        standard_mail_values["email_bcc"] = ''  # Don't send to all BCCs here
        mail_values_list.append(standard_mail_values)

        # 2. Individual BCC emails with simulated header
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue

            bcc_email = partner.email
            bcc_display = f'{partner.name} <{partner.email}>' if partner.name else partner.email

            bcc_mail_values = copy.deepcopy(mail_values)

            # Compose fake visible header for body
            fake_header = f"""
            <div style="color: #666; font-size: 13px; font-family: monospace;">
                <p><strong>From:</strong> {self.email_from or 'Lexora'}<br/>
                <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
                <strong>To:</strong> {to_display or '-'}<br/>
                <strong>Cc:</strong> {cc_display or '-'}<br/>
                <strong>Bcc:</strong> {bcc_display}<br/>
                <strong>Subject:</strong> {self.subject or '-'}</p>
                <p style="color:gray; font-style:italic;">🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply all.</p>
            </div>
            <br/>
            """

            original_body = bcc_mail_values.get('body', '')
            bcc_mail_values["body"] = fake_header + original_body
            bcc_mail_values["body_html"] = bcc_mail_values["body"]

            bcc_mail_values["email_to"] = bcc_email
            bcc_mail_values["email_cc"] = ''
            bcc_mail_values["email_bcc"] = ''

            mail_values_list.append(bcc_mail_values)

        return mail_values_list
