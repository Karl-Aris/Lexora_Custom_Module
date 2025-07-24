# ir_mail_server.py
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models
from email import encoders
from email.message import EmailMessage
from email.utils import parseaddr

_logger = logging.getLogger(__name__)

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Ensure Bcc recipient is handled properly: adds footer + correct smtp_to.
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
                    if part.get_content_maintype() == "text":
                        inject_bcc_footer(part)
            else:
                inject_bcc_footer(message)

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        # Override smtp_to only if this is a Bcc-specific message
        if x_odoo_bcc_value:
            bcc_email = parseaddr(x_odoo_bcc_value)[1]
            smtp_to_list = [bcc_email]
            _logger.debug("smtp_to set to Bcc only: %s", bcc_email)

        return smtp_from, smtp_to_list, message
