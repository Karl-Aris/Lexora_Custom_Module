from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee_applied = fields.Boolean(string="Authorize.Net Fee Applied", default=False)

    @api.model
    def _get_authorize_net_fee_product(self):
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def _remove_existing_authorize_net_fee(self, fee_product):
        self.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

    def _add_authorize_net_fee(self, fee_product):
        surcharge_amount = self.amount_untaxed * 0.035
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Payment Fee (3.5%)',
            'price_unit': round(surcharge_amount, 2),
            'product_uom_qty': 1,
            'tax_id': [(6, 0, [])],  # no tax
        })

    def apply_authorize_net_fee(self):
        for order in self:
            if order.authorize_fee_applied:
                continue

            provider_code = (order.payment_provider_id.code or '').lower().replace('.', '_')
            if provider_code == 'authorize_net':
                fee_product = order._get_authorize_net_fee_product()
                if not fee_product:
                    raise ValueError("Authorize.Net fee product (AUTH_NET_FEE) not found!")

                order._remove_existing_authorize_net_fee(fee_product)
                order._add_authorize_net_fee(fee_product)
                order.authorize_fee_applied = True
