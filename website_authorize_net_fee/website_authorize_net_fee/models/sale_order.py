from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_authorize_net_fee_product(self):
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def update_authorize_net_fee(self, use_fee):
        self.ensure_one()
        fee_product = self._get_authorize_net_fee_product()
        if not fee_product:
            return

        # Remove existing fee
        self.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

        if use_fee:
            fee = round(self.amount_untaxed * 0.035, 2)
            if fee > 0:
                self.order_line.create({
                    'order_id': self.id,
                    'product_id': fee_product.id,
                    'name': 'Authorize.Net Fee',
                    'product_uom_qty': 1,
                    'product_uom': fee_product.uom_id.id,
                    'price_unit': fee,
                    'tax_id': [(6, 0, fee_product.taxes_id.ids)],
                })
