from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee_added = fields.Boolean(default=False)

    def add_authorize_net_fee(self):
        self.ensure_one()
        if self.authorize_fee_added:
            return  # Prevent duplicate fee lines

        if self.state in ['sale', 'done']:
            return  # Don't add after confirmation

        fee_product = self.env.ref('payment_authorize_net_fee.product_authorize_net_fee', raise_if_not_found=False)
        if not fee_product:
            return

        # Remove existing line if any (for safety)
        existing = self.order_line.filtered(lambda l: l.product_id == fee_product)
        existing.unlink()

        fee_amount = self.amount_untaxed * 0.035
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': fee_product.name,
            'price_unit': round(fee_amount, 2),
            'product_uom_qty': 1,
            'product_uom': fee_product.uom_id.id,
            'tax_id': [(6, 0, fee_product.taxes_id.ids)],
        })

        self.authorize_fee_added = True
