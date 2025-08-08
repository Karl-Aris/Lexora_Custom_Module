from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_payment_transaction(self, vals):
        fee_product = self.env['product.product'].search([
            ('default_code', '=', 'AUTH_NET_FEE')
        ], limit=1)

        if vals.get('provider_id') and fee_product:
            provider = self.env['payment.provider'].browse(vals['provider_id'])
            if provider.code == 'authorize':
                # Remove old fee line
                self.order_line.filtered(
                    lambda l: l.product_id.id == fee_product.id
                ).unlink()

                fee = round(self.amount_untaxed * 0.035, 2)
                if fee > 0:
                    self.env['sale.order.line'].create({
                        'order_id': self.id,
                        'product_id': fee_product.id,
                        'name': fee_product.name,
                        'price_unit': fee,
                        'product_uom_qty': 1,
                    })

        return super()._create_payment_transaction(vals)
