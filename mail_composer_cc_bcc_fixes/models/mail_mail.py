# File: mail_mail_bcc_override/models/mail_mail.py

from odoo import models
import logging

_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _build_email(self, mail_values):
        """
        Override core _build_email method to force-inject 'bcc'
        so it reaches SMTP email object regardless of OCA interference.
        """
        message = super()._build_email(mail_values)

        if self.email_bcc:
            bcc_list = [e.strip() for e in self.email_bcc.split(',') if e.strip()]
            existing_bcc = message.get_all('Bcc', [])
            # Avoid duplicates
            for bcc in bcc_list:
                if bcc not in existing_bcc:
                    message['Bcc'] = message.get('Bcc', '') + (',' if message.get('Bcc') else '') + bcc
            _logger.info("Injected BCC into outgoing email: %s", message['Bcc'])

        return message
