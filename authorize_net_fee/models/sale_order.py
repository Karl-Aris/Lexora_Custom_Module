from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee_added = fields.Boolean(default=False)

    @api.onchange('payment_term_id')
    def _onchange_payment_method_fee(self):
        """Optional: Trigger fee addition if needed on change."""

    def add_authorize_net_fee(self):
        self.ensure_one()
        if self.authorize_fee_added:
            return

        provider = self.env.context.get('active_payment_provider')
        if provider != 'authorize':
            return

        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            raise UserError("Please create a product with Internal Reference = AUTH_NET_FEE")

        fee = self.amount_total * 0.035

        self.order_line = [(0, 0, {
            'product_id': fee_product.id,
            'name': fee_product.name,
            'price_unit': round(fee, 2),
            'product_uom_qty': 1,
        })]

        self.authorize_fee_added = True
