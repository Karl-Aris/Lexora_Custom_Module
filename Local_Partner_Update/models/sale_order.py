from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_studio_local = fields.Char(string="Is Local", compute="_compute_x_studio_local", store=True)

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
            state_val = ''
            state_source = ''
    
            if order.partner_id:
                if 'x_studio_state' in order.partner_id._fields and order.partner_id.x_studio_state:
                    state_val = order.partner_id.x_studio_state
                    state_source = 'x_studio_state'
                elif order.partner_id.state_id and order.partner_id.state_id.code:
                    state_val = order.partner_id.state_id.code
                    state_source = 'state_id.code'
    
            state_ok = state_val in allowed_states
    
            _logger.info(
                f\"[LOCAL_CHECK] Order: {order.name}, Partner: {order.partner_id.name}, "
                f\"State: {state_val} (from: {state_source}), Merchant OK: {merchant_ok}, State OK: {state_ok}\"
            )
    
            if merchant_ok and state_ok:
                order.x_studio_local = \"LOCAL\"
            else:
                order.x_studio_local = \"\"
