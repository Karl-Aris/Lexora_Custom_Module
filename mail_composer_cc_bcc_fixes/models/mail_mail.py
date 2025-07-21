from odoo import models
import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _build_email(self, mail_values):
        msg = super()._build_email(mail_values)
        if self.email_bcc:
            bcc_list = [e.strip() for e in self.email_bcc.split(',') if e.strip()]
            # Add a real Bcc header
            existing = msg.get_all('Bcc', [])
            for bcc in bcc_list:
                if bcc not in existing:
                    msg['Bcc'] = ', '.join(existing + bcc_list)
            _logger.info("Injected real BCC header: %s", msg['Bcc'])
        return msg
