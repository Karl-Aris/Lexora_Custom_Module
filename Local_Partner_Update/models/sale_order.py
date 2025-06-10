from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_studio_local = fields.Char(string="Is Local", compute="_compute_x_studio_local", store=True, readonly=True)

    @api.depends('partner_id')
    def _compute_x_studio_local(self):
        allowed_merchants = {
            'Bell+Modern Shopify',
            'Lore & Lane Amazon',
            'Bell+Modern Amazon',
            'Lexora Shopify',
            'Dealers',
            "Lowe's"
        }
        for order in self:
            if order.partner_id and order.partner_id.name in allowed_merchants:
                order.x_studio_local = "LOCAL"
            else:
                order.x_studio_local = ""
