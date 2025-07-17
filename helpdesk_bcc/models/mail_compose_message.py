
from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    bcc_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='mail_compose_message_res_partner_rel',
        column1='mail_compose_message_id',
        column2='partner_id',
        string='BCC Recipients'
    )
