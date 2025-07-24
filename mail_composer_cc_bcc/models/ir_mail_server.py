# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Define smtp_to based on context instead of To+Cc+Bcc.
        Also injects a note in the body for BCC recipients.
        """
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        # Add Bcc field inside message to pass validation
        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

            # Inject a body footer for BCC recipients
            bcc_html_notice = (
                "<br/><br/><hr/><p style='color:gray;'>"
                "<strong>Note:</strong> You received this message as a BCC recipient. "
                "Please do not reply to all."
                "</p>"
            )
            bcc_text_notice = (
                "\n\n---\nNote: You received this message as a BCC recipient. "
                "Please do not reply to all."
            )

            if message.is_multipart():
                for part in message.walk():
                    ctype = part.get_content_type()
                    charset = part.get_content_charset() or "utf-8"
                    if ctype == "text/html":
                        payload = part.get_payload(decode=True).decode(charset)
                        part.set_payload(payload + bcc_html_notice)
                        part.set_charset(charset)
                    elif ctype == "text/plain":
                        payload = part.get_payload(decode=True).decode(charset)
                        part.set_payload(payload + bcc_text_notice)
                        part.set_charset(charset)
            else:
                # Single-part message (not multipart)
                ctype = message.get_content_type()
                charset = message.get_content_charset() or "utf-8"
                payload = message.get_payload(decode=True).decode(charset)
                if ctype == "text/html":
                    message.set_payload(payload + bcc_html_notice)
                    message.set_charset(charset)
                else:
                    message.set_payload(payload + bcc_text_notice)
                    message.set_charset(charset)

            _logger.info("BCC footer injected for BCC: %s", x_odoo_bcc_value)

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
