from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_emails = fields.Char(string="BCC Emails", help="Comma-separated BCC addresses to include in all outgoing emails.")

    def message_post(self, **kwargs):
        if self.bcc_emails:
            bcc_list = [e.strip() for e in self.bcc_emails.split(',') if e.strip()]
            kwargs.setdefault('email_bcc', ','.join(bcc_list))
        return super().message_post(**kwargs)