from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sale_order_ids'):
                so_ids = vals['sale_order_ids'][0][2] if isinstance(vals['sale_order_ids'], list) else []
                if so_ids:
                    sale_orders = self.env['sale.order'].browse(so_ids)
                    fee_product = self.env['product.product'].search([
                        ('default_code', '=', 'AUTH_NET_FEE')
                    ], limit=1)
                    if fee_product:
                        for so in sale_orders:
                            provider_id = vals.get('provider_id') or so.payment_provider_id.id
                            if provider_id:
                                provider = self.env['payment.provider'].browse(provider_id)
                                if provider.code == 'authorize':
                                    # Remove old fee lines
                                    so.order_line.filtered(
                                        lambda l: l.product_id.id == fee_product.id
                                    ).unlink()
                                    # Add fee line
                                    fee = round(so.amount_untaxed * 0.035, 2)
                                    if fee > 0:
                                        self.env['sale.order.line'].create({
                                            'order_id': so.id,
                                            'product_id': fee_product.id,
                                            'name': fee_product.name,
                                            'price_unit': fee,
                                            'product_uom_qty': 1,
                                        })
        # Now create transaction after fee is added
        return super().create(vals_list)
