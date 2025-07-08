from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        email_from = self.team_id.x_alias_email_from
        if email_from:
            kwargs['email_from'] = email_from
        return super().message_post(**kwargs)
