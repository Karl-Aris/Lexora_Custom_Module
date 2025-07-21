from odoo import models
from odoo.addons.mail.models.mail_mail import MailDeliveryException

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            email = mail._build_email()
            if mail.email_bcc:
                bcc_list = [e.strip() for e in mail.email_bcc.split(',') if e.strip()]
                email['Bcc'] = ', '.join(bcc_list)  # Force Bcc into headers

            try:
                smtp_session = mail._get_smtp_session()
                smtp_session.send_message(email)
            except Exception as e:
                if raise_exception:
                    raise MailDeliveryException("Failed to send email.", e)
        return True
