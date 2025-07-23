from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    bcc_recipient_ids = fields.Many2many(
        'res.partner',
        string='Bcc',
        help='Partners who will receive a blind carbon copy of the email.'
    )
