from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_quotation_send(self):
        res = super().action_quotation_send()
        # Force reply_to only for sale order quotation
        if isinstance(res, dict) and res.get('context'):
            res['context'] = dict(res['context'])  # avoid modifying shared context
            res['context']['default_reply_to'] = 'erwinfabro@lexorahome.com'
        return res
