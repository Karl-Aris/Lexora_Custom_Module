from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        alias_email = self.team_id.alias_id and self.team_id.alias_id.alias_name
        if alias_email:
            domain = self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
            if domain:
                kwargs['email_from'] = f"{alias_email}@{domain}"
        return super().message_post(**kwargs)
