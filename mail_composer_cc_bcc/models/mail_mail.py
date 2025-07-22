# mail_mail.py
from odoo import models
from odoo.addons.mail.models.mail_mail import MailMail

def format_emails(emails):
    return ', '.join(emails) if emails else ''

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        # Send BCC emails individually so they are visible to each recipient
        mails_to_send = self.filtered(lambda m: m.state == 'outgoing')

        for mail in mails_to_send:
            bcc_list = mail.email_bcc.split(',') if mail.email_bcc else []
            if bcc_list:
                for bcc_email in bcc_list:
                    # Create a copy for each BCC recipient
                    mail_copy = mail.copy({
                        'email_to': bcc_email.strip(),
                        'email_bcc': False,  # Prevent recursion
                        'body_html': f'<p><strong>BCC:</strong> {bcc_email.strip()}</p>' + (mail.body_html or ''),
                    })
                    super(MailMail, mail_copy).send(auto_commit=auto_commit, raise_exception=raise_exception)
                mail.write({'state': 'sent'})
            else:
                super(MailMail, mail).send(auto_commit=auto_commit, raise_exception=raise_exception)

        return True
