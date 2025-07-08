from odoo import models
import re

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        alias = self.team_id.alias_id
        if alias:
            # Try to extract email from alias name or display_name
            match = re.search(r'<([^>]+)>', alias.name or alias.display_name or '')
            alias_email = match.group(1) if match else alias.name

            if alias_email:
                kwargs['email_from'] = alias_email
        return super().message_post(**kwargs)
