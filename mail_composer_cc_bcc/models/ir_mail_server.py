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
        x_odoo_bcc_value = next(
            (value for key, value in message._headers if key == "X-Odoo-Bcc"), None
        )

        if x_odoo_bcc_value:
            message["Bcc"] = x_odoo_bcc_value

        smtp_from, smtp_to_list, message = super()._prepare_email_message(
            message, smtp_session
        )

        if self.env.context.get("is_from_composer") and self.env.context.get("recipients"):
            smtp_to = self.env.context["recipients"].pop(0)
            smtp_to_list = [smtp_to]

        return smtp_from, smtp_to_list, message

