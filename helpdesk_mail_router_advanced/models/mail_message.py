from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        if values.get('model') == 'helpdesk.ticket' and values.get('res_id'):
            ticket = self.env['helpdesk.ticket'].browse(values['res_id'])
            if ticket.team_id and ticket.team_id.mail_server_id:
                values.setdefault('mail_server_id', ticket.team_id.mail_server_id.id)
        return super().create(values)