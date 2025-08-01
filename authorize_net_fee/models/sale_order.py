from odoo import models, fields, api

FEE_PERCENTAGE = 3.5
FEE_PRODUCT_NAME = 'Credit Card Fee'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_fee_product(self):
        product = self.env['product.product'].search([('name', '=', FEE_PRODUCT_NAME)], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': FEE_PRODUCT_NAME,
                'type': 'service',
                'list_price': 0.0,
            })
        return product

    def _remove_existing_fee_lines(self):
        self.order_line.filtered(lambda l: l.product_id.name == FEE_PRODUCT_NAME).unlink()

    def _add_authorize_net_fee(self):
        for order in self:
            # Check if Authorize.Net is the selected payment provider
            tx = order.transaction_ids.filtered(lambda t: t.state == 'draft')
            if tx and tx.provider_id.code == 'authorize_net':
                order._remove_existing_fee_lines()
                fee_product = order._get_fee_product()
                fee_amount = order.amount_untaxed * (FEE_PERCENTAGE / 100)
                order.order_line.create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': FEE_PRODUCT_NAME,
                    'product_uom_qty': 1,
                    'price_unit': fee_amount,
                })

    def _create_payment_transaction(self, *args, **kwargs):
        self._add_authorize_net_fee()
        return super()._create_payment_transaction(*args, **kwargs)
