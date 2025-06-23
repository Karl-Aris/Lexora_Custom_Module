from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    inventory_scan_mode = fields.Boolean(string="Enable Inventory Scan Mode")