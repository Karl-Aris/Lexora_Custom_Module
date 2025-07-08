from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        alias_email = self.team_id.alias_id.email if self.team_id.alias_id else None
        if alias_email:
            kwargs['email_from'] = alias_email
        return super().message_post(**kwargs)
