from odoo import models, fields, _
from odoo.exceptions import UserError


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    cc_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='mail_compose_cc_partner_rel',
        column1='compose_id',
        column2='partner_id',
        string='CC'
    )
    bcc_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='mail_compose_bcc_partner_rel',
        column1='compose_id',
        column2='partner_id',
        string='BCC'
    )

    def action_send_mail(self):
        email_to = ','.join(self.partner_ids.mapped('email'))
        email_cc = ','.join(self.cc_partner_ids.mapped('email'))
        email_bcc = ','.join(self.bcc_partner_ids.mapped('email'))

        if not any([email_to, email_cc, email_bcc]):
            raise UserError("Please specify at least one recipient.")

        subject = self.subject or '(No Subject)'
        body_html = self.body or ''
        email_from = self.env.user.email or 'noreply@example.com'
        reply_to = self.env.user.email or 'noreply@example.com'

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_to': email_to,
            'email_cc': email_cc,
            'email_bcc': email_bcc,
            'auto_delete': True,
            'email_from': email_from,
            'reply_to': reply_to,
        }

        res_model = self.model
        res_id = self.env.context.get('default_res_id')

        if res_model and res_id:
            mail_values.update({
                'res_model': res_model,
                'res_id': res_id,
            })

        mail = self.env['mail.mail'].sudo().create(mail_values)

        if not mail:
            raise UserError("Mail creation failed — check logs and values.")

        mail.send()
        return {'type': 'ir.actions.act_window_close'}
