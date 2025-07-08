from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.model == 'helpdesk.ticket' and mail.res_id:
                ticket = self.env['helpdesk.ticket'].browse(mail.res_id)
                if ticket.team_id and ticket.team_id.mail_server_id:
                    server = ticket.team_id.mail_server_id
                    if server.smtp_user:
                        mail.email_from = server.smtp_user
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)