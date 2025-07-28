from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def action_create_vendor_bill(self):
        # Implement your logic here or leave as placeholder
        return True