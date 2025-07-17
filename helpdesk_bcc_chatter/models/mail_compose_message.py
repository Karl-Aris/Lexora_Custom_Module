from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    partner_cc_ids = fields.Many2many(
        'res.partner',
        string="CC Partners",
        help="Optional CC recipients for messages"
    )
