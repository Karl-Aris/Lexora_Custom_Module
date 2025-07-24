# ir_mail_server.py
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models
from email import encoders
from email.message import EmailMessage

_logger = logging.getLogger(__name__)

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Define smtp_to based on context instead of To+Cc+Bcc.
        Append a note for Bcc recipients inside email body (MIME safe).
        Ensure Bcc recipient is added to smtp_to_list for actual delivery.
        """
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

            def inject_bcc_footer(part):
                content_type = part.get_content_type()
                charset = part.get_content_charset() or "utf-8"
                if content_type == "text/html":
                    html = part.get_payload(decode=True).decode(charset)
                    html += (
                        "<br><hr><small style=\"color:gray\">"
                        "Note: You are receiving this email as a Bcc recipient. "
                        "Please do not reply directly to this message."
                        "</small>"
                    )
                    part.set_payload(html.encode(charset))
                    if "Content-Transfer-Encoding" in part:
                        del part["Content-Transfer-Encoding"]
                    encoders.encode_base64(part)
                elif content_type == "text/plain":
                    text = part.get_payload(decode=True).decode(charset)
                    text += (
                        "\n\nNote: You are receiving this email as a Bcc recipient. "
                        "Please do not reply directly to this message."
                    )
                    part.set_payload(text.encode(charset))
                    if "Content-Transfer-Encoding" in part:
                        del part["Content-Transfer-Encoding"]
                    encoders.encode_base64(part)

            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_maintype() in ["text"]:
                        inject_bcc_footer(part)
            else:
                inject_bcc_footer(message)

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

            # Ensure Bcc recipient is in smtp_to_list if not already
            if x_odoo_bcc_value and smtp_to != x_odoo_bcc_value:
                smtp_to_list.append(x_odoo_bcc_value)
                _logger.debug("Appended Bcc smtp_to: %s", x_odoo_bcc_value)

        return smtp_from, smtp_to_list, message
