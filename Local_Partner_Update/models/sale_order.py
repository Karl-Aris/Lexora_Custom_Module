from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

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
        state_ok = False
        state_val = None

        if order.partner_id and 'x_studio_state' in order.partner_id._fields:
            state_val = order.partner_id.x_studio_state
            state_ok = state_val in allowed_states

        _logger.info(
            f"[LOCAL_CHECK] Order: {order.name}, Partner: {order.partner_id.name}, "
            f"State: {state_val}, Merchant OK: {merchant_ok}, State OK: {state_ok}"
        )

        if merchant_ok and state_ok:
            order.x_studio_local = "LOCAL"
        else:
            order.x_studio_local = ""
