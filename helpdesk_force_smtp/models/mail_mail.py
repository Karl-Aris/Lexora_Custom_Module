from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.model == 'helpdesk.ticket' and mail.res_id:
                ticket = self.env['helpdesk.ticket'].browse(mail.res_id)
                if ticket.team_id and ticket.team_id.mail_server_id:
                    mail.mail_server_id = ticket.team_id.mail_server_id.id
                    if ticket.team_id.alias_id and ticket.team_id.alias_id.display_name:
                        mail.email_from = ticket.team_id.alias_id.display_name
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)