from odoo import models, fields

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

        mail_values = {
            'subject': self.subject or '(No Subject)',
            'body_html': self.body or '',
            'email_to': email_to,
            'email_cc': email_cc,
            'email_bcc': email_bcc,
            'auto_delete': True,
            'email_from': self.env.user.email or 'noreply@example.com',
            'reply_to': self.env.user.email or 'noreply@example.com',
        }

        if self.model and self.res_id:
            mail_values['res_model'] = self.model
            mail_values['res_id'] = self.res_id

        self.env['mail.mail'].sudo().create(mail_values).send()
        return {'type': 'ir.actions.act_window_close'}
