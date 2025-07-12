from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _notify_get_reply_to(self, default=None):
        result = super()._notify_get_reply_to(default=default)
        for order in self:
            team = order.team_id
            reply_email = team.reply_to or team.email
            if reply_email:
                result[order.id] = self._notify_get_reply_to_formatted_email(
                    reply_email, order.name, company=order.company_id
                )
        return result
