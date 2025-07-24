# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import json
from odoo import models
from email.charset import Charset, QP
from email.message import EmailMessage

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message: EmailMessage, smtp_session):
        """
        Use custom X-Odoo-Bcc to inject note into the email body
        only for Bcc recipients (without changing headers).
        """
        headers = message.get("X-Odoo-Header")
        bcc_recipient = None

        try:
            headers_dict = json.loads(headers) if headers else {}
            bcc_recipient = headers_dict.get("X-Odoo-Bcc")
        except Exception as e:
            _logger.warning("Failed to parse X-Odoo-Header: %s", e)

        if bcc_recipient:
            # Add Bcc for compliance (even though not shown)
            message["Bcc"] = bcc_recipient

            # Inject notice in body
            bcc_html_note = (
                "<br/><br/><hr/><p><strong>🔒 You received this email as a BCC "
                "(Blind Carbon Copy). Please do not reply to all.</strong></p>"
            )
            bcc_text_note = (
                "\n\n---\n🔒 You received this email as a BCC "
                "(Blind Carbon Copy). Please do not reply to all."
            )
            utf8_charset = Charset("utf-8")
            utf8_charset.body_encoding = QP

            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        payload = part.get_payload(decode=True).decode(charset, errors="replace")
                    except Exception:
                        continue

                    if content_type == "text/html":
                        part.set_payload((payload + bcc_html_note).encode("utf-8"))
                        part.set_charset(utf8_charset)
                    elif content_type == "text/plain":
                        part.set_payload((payload + bcc_text_note).encode("utf-8"))
                        part.set_charset(utf8_charset)
            else:
                content_type = message.get_content_type()
                charset = message.get_content_charset() or "utf-8"
                try:
                    payload = message.get_payload(decode=True).decode(charset, errors="replace")
                except Exception:
                    payload = ""

                if content_type == "text/html":
                    message.set_payload((payload + bcc_html_note).encode("utf-8"))
                    message.set_charset(utf8_charset)
                elif content_type == "text/plain":
                    message.set_payload((payload + bcc_text_note).encode("utf-8"))
                    message.set_charset(utf8_charset)

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        # Preserve custom single-recipient behavior if enabled
        if self.env.context.get("is_from_composer") and self.env.context.get("recipients"):
            smtp_to = self.env.context["recipients"].pop(0)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
