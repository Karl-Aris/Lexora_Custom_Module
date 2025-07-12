from odoo import models, api

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        if not vals.get('reply_to') and vals.get('email_from'):
            vals['reply_to'] = vals['email_from']
        return super().create(vals)
