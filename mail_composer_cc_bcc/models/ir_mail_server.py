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
        Append a note for Bcc recipients inside email body.
        """
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        # Add Bcc field inside message to pass validation
        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

            # Inject note into body
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    charset = part.get_content_charset() or "utf-8"
                    if content_type == "text/html":
                        html = part.get_payload(decode=True).decode(charset)
                        html += ("<br><hr><small style=\"color:gray\">"
                                 "Note: You are receiving this email as a Bcc recipient. "
                                 "Please do not reply directly to this message." 
                                 "</small>")
                        part.set_payload(html.encode(charset))
                        if "Content-Transfer-Encoding" in part:
                            del part["Content-Transfer-Encoding"]
                        encoders.encode_base64(part)
                    elif content_type == "text/plain":
                        text = part.get_payload(decode=True).decode(charset)
                        text += ("\n\nNote: You are receiving this email as a Bcc recipient. "
                                 "Please do not reply directly to this message.")
                        part.set_payload(text.encode(charset))
                        if "Content-Transfer-Encoding" in part:
                            del part["Content-Transfer-Encoding"]
                        encoders.encode_base64(part)
            else:
                # Single-part email
                content_type = message.get_content_type()
                charset = message.get_content_charset() or "utf-8"
                if content_type == "text/html":
                    html = message.get_payload(decode=True).decode(charset)
                    html += ("<br><hr><small style=\"color:gray\">"
                             "Note: You are receiving this email as a Bcc recipient. "
                             "Please do not reply directly to this message." 
                             "</small>")
                    message.set_payload(html.encode(charset))
                    if "Content-Transfer-Encoding" in message:
                        del message["Content-Transfer-Encoding"]
                    encoders.encode_base64(message)
                elif content_type == "text/plain":
                    text = message.get_payload(decode=True).decode(charset)
                    text += ("\n\nNote: You are receiving this email as a Bcc recipient. "
                             "Please do not reply directly to this message.")
                    message.set_payload(text.encode(charset))
                    if "Content-Transfer-Encoding" in message:
                        del message["Content-Transfer-Encoding"]
                    encoders.encode_base64(message)

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_from_composer and self.env.context.get("recipients", False):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("smtp_to: %s", smtp_to)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
