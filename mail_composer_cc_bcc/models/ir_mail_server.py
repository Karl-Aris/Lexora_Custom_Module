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
        Inject BCC footer only for BCC recipients before delivery.
        """

        # Read the X-Odoo-Bcc header
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        # Inject BCC footer into body only when BCC recipient is being sent to
        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"][0]
            if x_odoo_bcc_value and smtp_to in x_odoo_bcc_value:
                # Prepare BCC footers
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
                        charset = part.get_content_charset() or "utf-8"
                        if content_type == "text/html":
                            payload = part.get_payload(decode=True).decode(charset, errors="replace")
                            part.set_payload((payload + bcc_html_footer).encode("utf-8"))
                            part.set_charset(utf8_charset)
                        elif content_type == "text/plain":
                            payload = part.get_payload(decode=True).decode(charset, errors="replace")
                            part.set_payload((payload + bcc_text_footer).encode("utf-8"))
                            part.set_charset(utf8_charset)
                else:
                    content_type = message.get_content_type()
                    charset = message.get_content_charset() or "utf-8"
                    payload = message.get_payload(decode=True).decode(charset, errors="replace")
                    if content_type == "text/html":
                        message.set_payload((payload + bcc_html_footer).encode("utf-8"))
                        message.set_charset(utf8_charset)
                    elif content_type == "text/plain":
                        message.set_payload((payload + bcc_text_footer).encode("utf-8"))
                        message.set_charset(utf8_charset)

        # Restore the original BCC header before sending
        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

        # Call super to finalize SMTP envelope (does not affect headers)
        smtp_from, smtp_to_list, message = super()._prepare_email_message(message, smtp_session)

        # Override SMTP recipient if from composer context
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
