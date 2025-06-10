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
            new_val = 'LOCAL' if order.partner_id.name in allowed_merchants else ''
            order.partner_id.write({'x_studio_local': new_val})

        return order
