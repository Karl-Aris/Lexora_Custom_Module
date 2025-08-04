from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def add_authorize_net_fee(self):
        """Add or update the Authorize.Net surcharge line on the Sale Order."""
        fee_product = self.env.ref('custom_authorize_net_fee.auth_net_fee_product', raise_if_not_found=False)
        if not fee_product:
            return

        self.ensure_one()

        # Remove existing surcharge line
        existing_line = self.order_line.filtered(lambda l: l.product_id.id == fee_product.id)
        if existing_line:
            existing_line.unlink()

        # Calculate fee amount
        fee_amount = self.amount_untaxed * 0.035
        if fee_amount <= 0:
            return

        # Add surcharge line
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Payment Fee (3.5%)',
            'product_uom_qty': 1,
            'price_unit': fee_amount,
        })
