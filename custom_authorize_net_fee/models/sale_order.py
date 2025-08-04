from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_authorize_net_fee_product(self):
        """Find the surcharge product by its default code."""
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def _remove_existing_authorize_net_fee(self, fee_product):
        """Remove existing surcharge lines to prevent duplicates."""
        self.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

    def _add_authorize_net_fee(self, fee_product):
        """Add the surcharge order line."""
        surcharge_amount = self.amount_untaxed * 0.035
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Payment Fee (3.5%)',
            'price_unit': surcharge_amount,
            'product_uom_qty': 1,
        })

    def apply_authorize_net_fee(self):
        """Call this method from your portal controller or payment confirmation hook."""
        for order in self:
            # Normalize provider code: lowercase + replace dot with underscore
            provider_code = (order.payment_provider_id.code or '').lower().replace('.', '_')
            if provider_code == 'authorize_net':
                fee_product = order._get_authorize_net_fee_product()
                if not fee_product:
                    raise ValueError("Authorize.Net fee product (AUTH_NET_FEE) not found!")
                order._remove_existing_authorize_net_fee(fee_product)
                order._add_authorize_net_fee(fee_product)
