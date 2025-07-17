from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="BCC Recipients",
        help="Partners who will be BCC'd on outgoing messages."
    )

    def message_post(self, **kwargs):
        if self.bcc_partner_ids:
            bcc_list = [p.email for p in self.bcc_partner_ids if p.email]
            if bcc_list:
                kwargs.setdefault('email_bcc', ','.join(bcc_list))
        return super().message_post(**kwargs)