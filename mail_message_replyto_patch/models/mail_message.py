
from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        # Set reply_to = email_from if not already set
        if not vals.get('reply_to') and vals.get('email_from'):
            vals['reply_to'] = vals['email_from']
        return super(MailMessage, self).create(vals)
