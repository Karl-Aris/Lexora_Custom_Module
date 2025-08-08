from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('payment_provider_id')
    def _onchange_payment_provider_id(self):
        """Add Authorize.Net surcharge when selected from the portal."""
        fee_product = self.env['product.product'].search([
            ('default_code', '=', 'AUTH_NET_FEE')
        ], limit=1)

        # Remove old surcharge lines
        if fee_product:
            self.order_line = self.order_line.filtered(
                lambda l: l.product_id.id != fee_product.id
            )

        if (
            self.payment_provider_id
            and self.payment_provider_id.code == 'authorize'
            and fee_product
        ):
            fee = round(self.amount_untaxed * 0.035, 2)
            if fee > 0:
                self.order_line += self.env['sale.order.line'].new({
                    'order_id': self.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'price_unit': fee,
                    'product_uom_qty': 1,
                })
