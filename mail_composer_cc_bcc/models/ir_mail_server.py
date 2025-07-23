import logging
from odoo import models

_logger = logging.getLogger(__name__)

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def _prepare_email_message(self, message, smtp_session):
        """
        Override to allow BCC messages to be sent to only one recipient.
        """
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"),
            None
        )

        # Set actual Bcc header only temporarily for RFC compliance
        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

        smtp_from, smtp_to_list, message = super()._prepare_email_message(message, smtp_session)

        if self.env.context.get("is_from_composer") and x_odoo_bcc_value:
            _logger.debug("Redirecting BCC-only mail to: %s", x_odoo_bcc_value)
            smtp_to_list = [x_odoo_bcc_value]

        return smtp_from, smtp_to_list, message
