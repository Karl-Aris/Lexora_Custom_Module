from odoo import models, fields

class IrFilters(models.Model):
    _inherit = "ir.filters"

    group_name = fields.Char(string="Filter Group")
