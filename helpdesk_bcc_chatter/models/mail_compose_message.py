# Optional patch to avoid crash if partner_cc_ids is referenced elsewhere
from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    partner_cc_ids = fields.Many2many('res.partner', string="CC (Unused)")
