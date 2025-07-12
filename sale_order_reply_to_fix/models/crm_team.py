from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    reply_to = fields.Char(string="Reply-To Email")