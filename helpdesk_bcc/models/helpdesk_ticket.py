
from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    bcc_partner_ids = fields.Many2many("res.partner", string="BCC Recipients")

    def message_post(self, **kwargs):
        if self.bcc_partner_ids:
            bcc_emails = ",".join(self.bcc_partner_ids.mapped("email"))
            kwargs.setdefault("email_bcc", bcc_emails)
        return super().message_post(**kwargs)
