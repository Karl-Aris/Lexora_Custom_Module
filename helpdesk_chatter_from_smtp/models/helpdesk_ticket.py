from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        smtp_user = self.env['ir.mail_server'].search([], limit=1).smtp_user
        if smtp_user:
            kwargs['email_from'] = smtp_user
        return super().message_post(**kwargs)
