from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def add_payment_fee_line(self, provider_code):
        self.ensure_one()
        self.order_line.filtered(lambda l: l.product_id.default_code == 'AUTH_NET_FEE').unlink()

        if provider_code == 'authorize':
            fee_product = self.env['product.product'].search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if fee_product:
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': 1.00,  # Update with dynamic logic if needed
                })
