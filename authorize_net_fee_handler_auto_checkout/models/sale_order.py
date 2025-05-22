from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super().create(vals)

        # Safe access: check if `payment_transaction_id` exists and is loaded
        transaction = order._context.get('payment_transaction_id') or order.payment_transaction_id
        if transaction and transaction.provider_id.code == 'authorize':
            product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
            if product:
                order.order_line.create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': 1,
                    'product_uom': product.uom_id.id,
                    'price_unit': order.amount_untaxed * 0.03,
                })

        return order
