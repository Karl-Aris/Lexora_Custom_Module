from odoo import models, fields, _
from odoo.exceptions import ValidationError


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

        res_model = self.model
        res_id = self.res_id or self.env.context.get('default_res_id')

        _logger.create({
            'name': 'PreMessageCreate',
            'type': 'server',
            'level': 'info',
            'dbname': self._cr.dbname,
            'message': f"[SEND TRIGGER] model={res_model}, id={res_id}",
            'path': __name__,
            'func': 'action_send_mail',
            'line': 0,
        })

        if not res_model or not res_id:
            raise ValidationError(_("Cannot send email: no linked record."))

        mail_values.update({
            'res_model': res_model,
            'res_id': res_id,
        })

        mail = self.env['mail.mail'].sudo().create(mail_values)

        _logger.create({
            'name': 'Mail Created',
            'type': 'server',
            'level': 'info',
            'dbname': self._cr.dbname,
            'message': f"[MAIL CREATED] ID: {mail.id} Subject: {mail.subject}",
            'path': __name__,
            'func': 'action_send_mail',
            'line': 0,
        })

        mail.send()
        return {'type': 'ir.actions.act_window_close'}
