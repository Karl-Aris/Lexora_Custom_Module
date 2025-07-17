from odoo import models

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send(self, auto_commit=False, raise_exception=False):
        for mail in self:
            if mail.model == 'helpdesk.ticket' and mail.res_id:
                ticket = self.env['helpdesk.ticket'].sudo().browse(mail.res_id)
                if ticket.bcc_partner_ids:
                    mail.bcc = ','.join(ticket.bcc_partner_ids.mapped('email'))
        return super()._send(auto_commit=auto_commit, raise_exception=raise_exception)
