# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models
from email.charset import Charset, QP
from email.message import EmailMessage

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message: EmailMessage, smtp_session):
        """
        Inject BCC footer for BCC recipients only.
        Keep header unchanged for To and Cc.
        """
        # Restore original Bcc from X-Odoo-Bcc if set
        x_odoo_bcc = next((v for k, v in message._headers if k == "X-Odoo-Bcc"), None)
        if x_odoo_bcc:
            message["Bcc"] = x_odoo_bcc

        smtp_from, smtp_to_list, message = super()._prepare_email_message(message, smtp_session)

        # Check if we're sending to a BCC recipient
        bcc_recipients = []
        if x_odoo_bcc:
            bcc_recipients = [e.strip() for e in x_odoo_bcc.split(",")]

        if any(rcpt in bcc_recipients for rcpt in smtp_to_list):
            # Add BCC note to body
            bcc_html_footer = (
                "<br/><br/><hr/><p><strong>🔒 You received this email as a BCC "
                "(Blind Carbon Copy). Please do not reply to all.</strong></p>"
            )
            bcc_text_footer = (
                "\n\n---\n🔒 You received this email as a BCC "
                "(Blind Carbon Copy). Please do not reply to all."
            )
            utf8_charset = Charset("utf-8")
            utf8_charset.body_encoding = QP

            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        payload = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                        part.set_payload((payload + bcc_html_footer).encode("utf-8"))
                        part.set_charset(utf8_charset)
                    elif content_type == "text/plain":
                        payload = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                        part.set_payload((payload + bcc_text_footer).encode("utf-8"))
                        part.set_charset(utf8_charset)
            else:
                content_type = message.get_content_type()
                payload = message.get_payload(decode=True).decode(message.get_content_charset() or "utf-8", errors="replace")
                if content_type == "text/html":
                    message.set_payload((payload + bcc_html_footer).encode("utf-8"))
                    message.set_charset(utf8_charset)
                elif content_type == "text/plain":
                    message.set_payload((payload + bcc_text_footer).encode("utf-8"))
                    message.set_charset(utf8_charset)

        return smtp_from, smtp_to_list, message
