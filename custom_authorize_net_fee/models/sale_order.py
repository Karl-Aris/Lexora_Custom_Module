from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee_applied = fields.Boolean(string="Authorize.Net Fee Applied", default=False)

    @api.model
    def _get_authorize_net_fee_product(self):
        """Find the Authorize.Net surcharge product by default code."""
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def _remove_existing_authorize_net_fee(self, fee_product):
        """Remove any existing Authorize.Net fee lines."""
        self.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

    def _add_authorize_net_fee(self, fee_product):
        """Add the 3.5% surcharge line to the order."""
        surcharge_amount = round(self.amount_untaxed * 0.035, 2)
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Payment Fee (3.5%)',
            'price_unit': surcharge_amount,
            'product_uom_qty': 1,
            'tax_id': [(6, 0, [])],  # No tax
        })

    def apply_authorize_net_fee(self):
        """Apply the Authorize.Net fee if applicable and not already added."""
        for order in self:
            # Avoid duplicate application
            if order.authorize_fee_applied:
                _logger.info("Authorize.Net fee already applied to order %s", order.name)
                continue

            # Defensive check
            if not order.payment_provider_id:
                _logger.warning("No payment provider set on order %s; skipping fee", order.name)
                continue

            provider_code = (order.payment_provider_id.code or '').lower().replace('.', '_')
            if provider_code != 'authorize_net':
                _logger.info("Payment provider is not Authorize.Net on order %s", order.name)
                continue

            fee_product = order._get_authorize_net_fee_product()
            if not fee_product:
                raise ValueError("Authorize.Net fee product with default_code 'AUTH_NET_FEE' not found!")

            _logger.info("Applying Authorize.Net fee to order %s", order.name)

            order._remove_existing_authorize_net_fee(fee_product)
            order._add_authorize_net_fee(fee_product)
            order.authorize_fee_applied = True
