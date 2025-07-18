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
        self.env['mail.mail'].create({
            'subject': self.subject or '(No Subject)',
            'body_html': self.body or '',
            'email_to': ','.join(self.partner_ids.mapped('email')),
            'email_cc': ','.join(self.cc_partner_ids.mapped('email')),
            'email_bcc': ','.join(self.bcc_partner_ids.mapped('email')),
            'auto_delete': True,
            'res_model': self.model,
            'res_id': self.res_id,
        }).send()
        return {'type': 'ir.actions.act_window_close'}
