from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)

        # Get the surcharge product once instead of querying for each transaction
        fee_product = self.env['product.product'].search([
            ('default_code', '=', 'AUTH_NET_FEE')
        ], limit=1)

        for tx in transactions:
            if (
                tx.provider_id.code == 'authorize'
                and tx.sale_order_ids
                and fee_product
            ):
                for so in tx.sale_order_ids:
                    # Remove previous surcharge lines (ensure we match by ID to avoid ORM caching issues)
                    so.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()

                    fee = round(so.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        self.env['sale.order.line'].create({
                            'order_id': so.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })

        return transactions
