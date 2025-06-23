from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_type_id.code == 'internal' and not self.env.user.has_group('inventory_adjustment_restrictor.group_can_adjust_inventory'):
            raise UserError(_("You are not allowed to validate internal transfers."))
        return super().button_validate()