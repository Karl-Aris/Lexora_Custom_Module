from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _notify_get_reply_to(self, default=None):
        result = super()._notify_get_reply_to(default=default)
        for order in self:
            team_reply = order.team_id.reply_to or order.team_id.email
            if team_reply:
                result[order.id] = self._notify_get_reply_to_formatted_email(
                    team_reply, order.name, company=order.company_id
                )
        return result