from odoo import models, fields, api

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    bcc = fields.Char('BCC')

    @api.model
    def create(self, vals):
        if vals.get('bcc'):
            self = super().create(vals)
            self = self.with_context(bcc=vals['bcc'])
            return self
        return super().create(vals)

    def send_mail(self, auto_commit=False):
        res = super().send_mail(auto_commit=auto_commit)
        bcc = self.bcc
        if bcc:
            mail_mail = self.env['mail.mail'].search([('mail_message_id', 'in', self.mail_ids.ids)])
            mail_mail.write({'email_bcc': bcc})
        return res