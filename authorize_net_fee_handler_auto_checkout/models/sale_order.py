from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _authorize_net_add_fee(self, order):
        """ Adds Authorize.Net surcharge to the order """
        authnet_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not authnet_product:
            return

        # Check if surcharge line already exists
        if any(line.product_id == authnet_product for line in order.order_line):
            return

        fee_amount = order.amount_total * 0.03
        order.order_line.create({
            'order_id': order.id,
            'product_id': authnet_product.id,
            'name': 'Authorize.Net Surcharge',
            'product_uom_qty': 1,
            'product_uom': authnet_product.uom_id.id,
            'price_unit': fee_amount,
        })

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.payment_transaction_id and order.payment_transaction_id.provider_id.code == 'authorize':
                self._authorize_net_add_fee(order)
        return orders
