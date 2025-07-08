from odoo import models, fields

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    mail_server_id = fields.Many2one('ir.mail_server', string="Outgoing Mail Server")
