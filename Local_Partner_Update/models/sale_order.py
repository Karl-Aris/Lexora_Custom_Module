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
        allowed_states = {'PA', 'NY', 'NJ', 'MD', 'VA', 'DC', 'WV', 'OH'}

        for order in self:
            merchant_ok = order.partner_id and order.partner_id.name in allowed_merchants
            state_ok = order.partner_id and order.partner_id.x_studio_state in allowed_states

            if merchant_ok and state_ok:
                order.x_studio_local = "LOCAL"
            else:
                order.x_studio_local = ""
