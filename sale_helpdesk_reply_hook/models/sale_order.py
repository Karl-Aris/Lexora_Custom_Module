from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def message_post(self, **kwargs):
        if kwargs.get('message_type') == 'email':
            kwargs['reply_to'] = 'dump.lexora@lexorahome.com'
        return super().message_post(**kwargs)
