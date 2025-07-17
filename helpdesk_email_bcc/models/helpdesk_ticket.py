from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many('res.partner', string='BCC Recipients')

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        for ticket in self:
            if ticket.bcc_partner_ids:
                self.env['mail.mail'].create({
                    'subject': res.subject or ticket.name,
                    'body_html': res.body or '',
                    'model': ticket._name,
                    'res_id': ticket.id,
                    'email_from': self.env.user.email,
                    'email_to': '',  # real recipients hidden
                    'email_bcc': ','.join(ticket.bcc_partner_ids.mapped('email')),
                }).send()
        return res
