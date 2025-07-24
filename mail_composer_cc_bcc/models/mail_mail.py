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
        Define smtp_to based on context instead of To+Cc+Bcc.
        Also inject BCC notice into body for BCC recipients.
        """
        # Grab BCC recipient from header
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

        # Inject BCC footer *before* sending
        if x_odoo_bcc_value:
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

        # Use original logic to set SMTP target
        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
