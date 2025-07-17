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
                composer = self.env['mail.compose.message'].with_context({
                    'default_model': 'helpdesk.ticket',
                    'default_res_ids': [ticket.id],
                    'default_partner_ids': ticket.bcc_partner_ids.ids,
                }).create({
                    'body': kwargs.get('body') or '',
                    'subject': kwargs.get('subject') or ticket.name,
                })
                composer.action_send_mail()
        return message

