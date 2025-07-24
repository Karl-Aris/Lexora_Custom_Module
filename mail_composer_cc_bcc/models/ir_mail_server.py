from odoo import models
import logging

_logger = logging.getLogger(__name__)

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Set smtp_to based on context and inject BCC notice for BCC recipients only.
        """
        # Detect BCC recipient
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value  # Needed for RFC compliance (even if hidden)

            # Prepare BCC footer
            bcc_html_footer = (
                "<br/><br/><hr/><p style='color:gray;'>"
                "<strong>Note:</strong> You received this email as a BCC (Blind Carbon Copy) recipient. "
                "Please do not reply to all.</p>"
            )
            bcc_text_footer = (
                "\n\n---\nNote: You received this email as a BCC (Blind Carbon Copy) recipient. "
                "Please do not reply to all."
            )

            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() in ("text/html", "text/plain"):
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            payload = part.get_payload(decode=True).decode(charset)
                        except (UnicodeDecodeError, LookupError):
                            payload = part.get_payload(decode=True).decode("utf-8", errors="replace")
                            charset = "utf-8"

                        if part.get_content_type() == "text/html":
                            part.set_payload(payload + bcc_html_footer)
                        else:
                            part.set_payload(payload + bcc_text_footer)

                        part.set_charset("utf-8")
            else:
                charset = message.get_content_charset() or "utf-8"
                try:
                    payload = message.get_payload(decode=True).decode(charset)
                except (UnicodeDecodeError, LookupError):
                    payload = message.get_payload(decode=True).decode("utf-8", errors="replace")
                    charset = "utf-8"

                if message.get_content_type() == "text/html":
                    message.set_payload(payload + bcc_html_footer)
                else:
                    message.set_payload(payload + bcc_text_footer)

                message.set_charset("utf-8")

            _logger.debug("BCC footer injected for: %s", x_odoo_bcc_value)

        # Continue with original behavior
        smtp_from, smtp_to_list, message = super()._prepare_email_message(message, smtp_session)

        if self.env.context.get("is_from_composer") and self.env.context.get("recipients"):
            smtp_to = self.env.context["recipients"].pop(0)
            _logger.debug("SMTP routed to single recipient: %s", smtp_to)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message
