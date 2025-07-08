from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        alias = self.team_id.alias_id
        domain = self.env['ir.config_parameter'].sudo().get_param('mail.catchall.domain')
        if alias and domain:
            kwargs['email_from'] = f"{alias.alias_name}@{domain}"
        return super().message_post(**kwargs)
