from odoo import models, fields

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    x_alias_email_from = fields.Char(string="Alias Email From")
