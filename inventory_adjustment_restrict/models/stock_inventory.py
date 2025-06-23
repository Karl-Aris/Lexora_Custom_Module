from odoo import models, api, _
from odoo.exceptions import UserError

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def create(self, vals):
        user = self.env.user
        company = self.env.company

        if not user.has_group('inventory_adjustment_restrict.group_inventory_scan') and not company.inventory_scan_mode:
            raise UserError(_("Inventory Adjustments are only allowed during scheduled warehouse scans."))

        return super().create(vals)
