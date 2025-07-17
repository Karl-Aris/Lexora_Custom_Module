from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many('res.partner', string='BCC Recipients')

    def action_send_bcc_email(self):
        for ticket in self:
            bcc_emails = ','.join(ticket.bcc_partner_ids.mapped('email'))
            if not bcc_emails:
                continue

            # use mail.compose.message wizard
            compose = self.env['mail.compose.message'].with_context(
                default_model='helpdesk.ticket',
                default_res_id=ticket.id,
                default_use_template=False,
                default_composition_mode='comment',
            ).create({
                'subject': f"Ticket #{ticket.id}: {ticket.name}",
                'body': ticket.description or 'No content',
                'email_to': '',  # no visible TO recipient
                'email_bcc': bcc_emails,  # ✅ supported here
            })
            compose.send_mail()
