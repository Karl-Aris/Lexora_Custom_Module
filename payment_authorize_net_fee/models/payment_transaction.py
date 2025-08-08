from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _create_transaction(self, vals):
        provider_id = vals.get('provider_id')
        provider = self.env['payment.provider'].browse(provider_id) if provider_id else None

        # Only apply for Authorize.Net provider
        if provider and provider.code == 'authorize_net':
            for order in self:
                # Check if fee already exists
                fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
                if fee_product and not order.order_line.filtered(lambda l: l.product_id == fee_product):
                    fee_amount = order.amount_total * 0.035
                    order.order_line = [(0, 0, {
                        'product_id': fee_product.id,
                        'product_uom_qty': 1,
                        'price_unit': fee_amount,
                        'name': fee_product.name
                    })]
                    order._amount_all()  # Recompute totals

                # Force updated total into the transaction values
                vals['amount'] = order.amount_total

        return super(SaleOrder, self)._create_transaction(vals)
