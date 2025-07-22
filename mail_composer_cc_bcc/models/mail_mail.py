# mail_mail.py

from odoo import models
from email.utils import formataddr
from email.header import Header

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send(self, auto_commit=False, raise_exception=False):
        # Call original _send but patch msg to include visible BCC
        for mail in self:
            if not mail.email_from or (not mail.email_to and not mail.email_cc and not mail.email_bcc):
                continue

            # Generate the message before sending
            msg = mail._prepare_email()

            # Inject visible BCC (so recipients see it)
            if mail.email_bcc:
                bcc_formatted = ', '.join([
                    formataddr((str(Header(p.split('<')[0].strip(), 'utf-8')), p.split('<')[-1].replace('>', '').strip()))
                    if '<' in p else p
                    for p in mail.email_bcc.split(',')
                ])
                msg['Bcc'] = bcc_formatted

            # Send the email
            smtp_session = mail._get_smtp_session()
            try:
                smtp_session.send_message(msg)
                mail.write({'state': 'sent'})
            finally:
                smtp_session.quit()
