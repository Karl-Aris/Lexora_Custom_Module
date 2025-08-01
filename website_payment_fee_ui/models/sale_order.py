# models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _remove_existing_fee_line(self, fee_product):
        """Remove existing fee line (by product)."""
        self.ensure_one()
        self.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

    def _add_payment_fee_line(self, fee_product, percentage):
        """Add fee line based on selected provider's percentage."""
        self.ensure_one()
        fee_amount = self.amount_untaxed * (percentage / 100.0)

        self.env['sale.order.line'].create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': f'{fee_product.name} ({percentage}%)',
            'product_uom_qty': 1,
            'product_uom': fee_product.uom_id.id,
            'price_unit': fee_amount,
        })
