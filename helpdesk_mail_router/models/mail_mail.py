from odoo import models, api

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        if 'model' in vals and vals['model'] == 'helpdesk.ticket' and 'res_id' in vals:
            ticket = self.env['helpdesk.ticket'].browse(vals['res_id'])
            if ticket.team_id:
                if ticket.team_id.alias_id:
                    vals['email_from'] = ticket.team_id.alias_id.display_name

                if ticket.team_id.mail_server_id:
                    vals['mail_server_id'] = ticket.team_id.mail_server_id.id

                if ticket.email:
                    vals['reply_to'] = ticket.email

                if ticket.message_ids:
                    last_msg_id = ticket.message_ids[-1].message_id
                    if last_msg_id:
                        vals['headers'] = vals.get('headers', {})
                        vals['headers']['In-Reply-To'] = last_msg_id
                        vals['headers']['References'] = last_msg_id

        return super(MailMail, self).create(vals)