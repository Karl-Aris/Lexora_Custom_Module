# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from email.charset import Charset, QP
from email.mime.text import MIMEText
from odoo import models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Define smtp_to based on context instead of To+Cc+Bcc,
        and inject footer for BCC recipients without cloning the message.
        """
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        # Add Bcc field to headers for RFC compliance (SMTP hides it, but we need it present)
        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

        # Determine smtp_from, smtp_to, and get the original MIMEMessage
        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        # Handle BCC payload only for messages coming from mail composer
        is_from_composer = self.env.context.get("is_from_composer", False)
        bcc_recipients = self.env.context.get("recipients", [])

        if is_from_composer and bcc_recipients:
            smtp_to = bcc_recipients.pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

            if x_odoo_bcc_value and smtp_to == x_odoo_bcc_value:
                # Create footers
                bcc_html_footer = (
                    "<br/><br/><hr/><p><strong>🔒 You received this email as a "
                    "BCC (Blind Carbon Copy). Please do not reply to all.</strong></p>"
                )
                bcc_text_footer = (
                    "\n\n---\n🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all."
                )

                # Prepare charset
                utf8_charset = Charset("utf-8")
                utf8_charset.body_encoding = QP  # quoted-printable is email-safe

                # Multipart: inject into text/plain or text/html parts
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_maintype() == "text":
                            subtype = part.get_content_subtype()
                            footer = bcc_html_footer if subtype == "html" else bcc_text_footer
                            try:
                                charset = part.get_content_charset() or "utf-8"
                                payload = part.get_payload(decode=True).decode(charset)
                            except Exception:
                                payload = part.get_payload(decode=True).decode("utf-8", errors="replace")

                            part.set_payload((payload + footer).encode("utf-8"))
                            part.set_charset(utf8_charset)

                else:
                    # Single-part message
                    subtype = message.get_content_subtype()
                    footer = bcc_html_footer if subtype == "html" else bcc_text_footer
                    try:
                        charset = message.get_content_charset() or "utf-8"
                        payload = message.get_payload(decode=True).decode(charset)
                    except Exception:
                        payload = message.get_payload(decode=True).decode("utf-8", errors="replace")

                    message.set_payload((payload + footer).encode("utf-8"))
                    message.set_charset(utf8_charset)

        return smtp_from, smtp_to_list, message
