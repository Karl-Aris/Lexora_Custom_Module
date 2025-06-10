from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)

        allowed_merchants = {
            'Bell+Modern Shopify',
            'Lore & Lane Amazon',
            'Bell+Modern Amazon',
            'Lexora Shopify',
            'Dealers',
            "Lowe's"
        }

        if order.partner_id:
            if order.partner_id.name in allowed_merchants:
                order.partner_id.x_studio_local = "LOCAL"
            else:
                order.partner_id.x_studio_local = ""

        return order
