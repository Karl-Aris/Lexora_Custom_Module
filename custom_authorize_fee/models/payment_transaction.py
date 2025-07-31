from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def post_process_after_done(self):
        res = super().post_process_after_done()

        for tx in self:
            acquirer = tx.acquirer_id
            if acquirer.provider != 'authorize':
                continue

            fee_percent = acquirer.fees_domestic_percent or 0.0
            if not fee_percent:
                continue

            fee_amount = tx.amount * fee_percent / 100.0

            fee_product = self.env['product.product'].search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if not fee_product:
                continue

            for sale_order in tx.sale_order_ids:
                if any(line.product_id.id == fee_product.id for line in sale_order.order_line):
                    continue

                sale_order.order_line.create({
                    'order_id': sale_order.id,
                    'product_id': fee_product.id,
                    'name': 'Authorize.Net Processing Fee',
                    'price_unit': round(fee_amount, 2),
                    'product_uom_qty': 1,
                })

        return res