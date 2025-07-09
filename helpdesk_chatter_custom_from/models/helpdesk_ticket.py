from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_get_email_values(self, notifications):
        res = super().message_get_email_values(notifications)
        for ticket, values in res.items():
            team = ticket.team_id
            if team and team.x_alias_email_from:
                values['email_from'] = team.x_alias_email_from
                # DO NOT override reply_to – Odoo will handle threading
        return res
