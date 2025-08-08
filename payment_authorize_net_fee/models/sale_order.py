from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_provider_id = fields.Many2one('payment.provider', string="Payment Provider")
    
    def _get_authorize_fee_product(self):
        return self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

    def _update_authorize_fee_line(self):
        self.ensure_one()
        fee_product = self._get_authorize_fee_product()
        if not fee_product:
            return

        fee_line = self.order_line.filtered(lambda l: l.product_id == fee_product)
        is_authorize = self.payment_provider_id and self.payment_provider_id.code == 'authorize'

        if is_authorize:
            fee_amount = self.amount_untaxed * 0.035
            if fee_amount <= 0:
                if fee_line:
                    fee_line.unlink()
                return

            if fee_line:
                fee_line.write({
                    'price_unit': fee_amount,
                    'product_uom_qty': 1,
                })
            else:
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': fee_amount,
                    'product_uom': fee_product.uom_id.id,
                })
        else:
            if fee_line:
                fee_line.unlink()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_authorize_fee_line()
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'payment_provider_id' in vals or 'order_line' in vals:
            for order in self:
                order._update_authorize_fee_line()
        return res
