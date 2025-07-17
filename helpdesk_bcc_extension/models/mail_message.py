from odoo import models, fields

class MailMessage(models.Model):
    _inherit = 'mail.message'

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'mail_message_bcc_partner_rel',
        'message_id',
        'partner_id',
        string='BCC Recipients'
    )
