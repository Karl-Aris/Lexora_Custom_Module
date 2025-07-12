
from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _notify_prepare_email_values(self, message):
        values = super()._notify_prepare_email_values(message)
        values['reply_to'] = 'orders@lexorahome.com'
        return values
