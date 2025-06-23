from odoo import models, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        self._check_inventory_adjustment_access()
        return super().create(vals)

    def write(self, vals):
        self._check_inventory_adjustment_access()
        return super().write(vals)

    def _check_inventory_adjustment_access(self):
        user = self.env.user
        company = self.env.company

        if not user.has_group('inventory_adjustment_restrict.group_inventory_scan') and not company.inventory_scan_mode:
            raise UserError(_("Inventory adjustments are only allowed during warehouse scan sessions."))
