from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_authorize_net_fee(self):
        """Adds a 3.5% surcharge line to the sale order if using Authorize.Net."""
        self.ensure_one()

        fee_product = self.env['product.product'].search(
            [('default_code', '=', 'AUTH_NET_FEE')], limit=1
        )
        if not fee_product:
            return

        # Remove previous surcharge lines (avoid duplicates)
        self.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

        # Add fee line
        fee_amount = self.amount_untaxed * 0.035
        if fee_amount <= 0:
            return

        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': fee_product.name,
            'price_unit': round(fee_amount, 2),
            'product_uom_qty': 1.0,
        })
