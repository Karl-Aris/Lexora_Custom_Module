from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="BCC Recipients",
        help="Partners who will be BCC'd on outgoing messages."
    )

    def message_post(self, **kwargs):
        message = super().message_post(**kwargs)
        for ticket in self:
            if ticket.bcc_partner_ids:
                bcc_emails = [p.email for p in ticket.bcc_partner_ids if p.email]
                if bcc_emails and ticket.partner_id and ticket.partner_id.email:
                    self.env['mail.mail'].create({
                        'subject': kwargs.get('subject') or ticket.name,
                        'body_html': kwargs.get('body') or '',
                        'email_to': ticket.partner_id.email,
                        'email_bcc': ','.join(bcc_emails),
                        'model': self._name,
                        'res_id': ticket.id,
                        'auto_delete': True,
                    }).send()
        return message