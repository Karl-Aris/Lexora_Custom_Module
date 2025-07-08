from odoo import models
import re

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        alias = self.team_id.alias_id
        if alias:
            # Try to extract from alias_display_name
            raw = alias.alias_display_name or alias.alias_name
            match = re.search(r'<([^>]+)>', raw)
            alias_email = match.group(1) if match else raw

            if alias_email:
                kwargs['email_from'] = alias_email
        return super().message_post(**kwargs)
