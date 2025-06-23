from odoo import models, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('inventory_adjustment_restrictor.group_can_adjust_inventory'):
            raise UserError(_("You are not allowed to create stock quants (Inventory Adjustment is restricted)."))
        return super().create(vals)

    def write(self, vals):
        if not self.env.user.has_group('inventory_adjustment_restrictor.group_can_adjust_inventory'):
            raise UserError(_("You are not allowed to modify stock quants (Inventory Adjustment is restricted)."))
        return super().write(vals)