from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_fee = fields.Monetary(string="Authorize.net Fee", currency_field='currency_id')

    @api.depends('payment_acquirer_id', 'amount_untaxed')
    def _compute_authorize_fee(self):
        for order in self:
            if order.payment_acquirer_id and 'authorize' in order.payment_acquirer_id.provider:
                order.authorize_fee = order.amount_untaxed * 0.03
            else:
                order.authorize_fee = 0

    @api.depends('order_line.price_total', 'authorize_fee')
    def _amount_all(self):
        super()._amount_all()
        for order in self:
            order.amount_total += order.authorize_fee

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.authorize_fee > 0:
                fee_product = self.env.ref('custom_authorize_fee.product_authorize_fee', raise_if_not_found=False)
                if fee_product:
                    self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': fee_product.id,
                        'name': 'Authorize.Net Surcharge',
                        'price_unit': order.authorize_fee,
                        'product_uom_qty': 1,
                    })
        return res
