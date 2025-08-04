from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee_applied = fields.Boolean(string="Authorize.Net Fee Applied", default=False)

    @api.model
    def _get_authorize_net_fee_product(self):
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def _remove_existing_authorize_net_fee(self, fee_product):
        self.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

    def _add_authorize_net_fee(self, fee_product):
        surcharge_amount = round(self.amount_untaxed * 0.035, 2)
        _logger.info("Calculated Authorize.Net surcharge: %.2f", surcharge_amount)
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Payment Fee (3.5%)',
            'price_unit': surcharge_amount,
            'product_uom_qty': 1,
            'tax_id': [(6, 0, [])],
        })

    def apply_authorize_net_fee(self):
        for order in self:
            _logger.info("Checking if Authorize.Net fee should be applied to order %s", order.name)

            if order.authorize_fee_applied:
                _logger.info("Fee already applied on order %s", order.name)
                continue

            if not order.payment_provider_id:
                _logger.warning("No payment provider on order %s", order.name)
                continue

            provider_code = (order.payment_provider_id.code or '').lower().replace('.', '_')
            _logger.info("Provider code for order %s is %s", order.name, provider_code)

            if provider_code != 'authorize_net':
                _logger.info("Provider is not Authorize.Net, skipping fee for %s", order.name)
                continue

            fee_product = order._get_authorize_net_fee_product()
            if not fee_product:
                _logger.error("Authorize.Net fee product with default_code 'AUTH_NET_FEE' not found!")
                raise ValueError("Authorize.Net fee product with default_code 'AUTH_NET_FEE' not found!")

            _logger.info("Applying Authorize.Net fee to order %s", order.name)
            order._remove_existing_authorize_net_fee(fee_product)
            order._add_authorize_net_fee(fee_product)
            order.authorize_fee_applied = True
