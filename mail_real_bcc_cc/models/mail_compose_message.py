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

        _logger = self.env['ir.logging']
        _logger.create({
            'name': 'Mail Real BCC Debug',
            'type': 'server',
            'level': 'info',
            'dbname': self._cr.dbname,
            'message': f"[BCC PATCH] To: {email_to} CC: {email_cc} BCC: {email_bcc}",
            'path': __name__,
            'func': 'action_send_mail',
            'line': 0,
        })

        res_model = self.model
        res_id = self.env.context.get('default_res_id')

        if res_model and res_id:
            self.env['mail.message'].create({
                'model': res_model,
                'res_id': res_id,
                'subject': self.subject or '(No Subject)',
                'body': self.body or '',
                'email_from': self.env.user.email or 'noreply@example.com',
                'reply_to': self.env.user.email or 'noreply@example.com',
                'message_type': 'email',
                'partner_ids': [(4, p.id) for p in self.partner_ids],
                'cc_partner_ids': [(4, p.id) for p in self.cc_partner_ids],
                'bcc_partner_ids': [(4, p.id) for p in self.bcc_partner_ids],
            })._notify(force_send=True, send_after_commit=True)

        return {'type': 'ir.actions.act_window_close'}
