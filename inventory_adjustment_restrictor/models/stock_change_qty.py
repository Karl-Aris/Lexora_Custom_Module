from odoo import models, _
from odoo.exceptions import UserError

class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    def action_apply(self):
        if not self.env.user.has_group('inventory_adjustment_restrictor.group_can_adjust_inventory'):
            raise UserError(_("You are not allowed to perform inventory adjustments."))
        return super().action_apply()