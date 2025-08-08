from odoo import models, api

class WebsiteSaleAuthorizeFee(models.Model):
    _inherit = 'website.sale'

    @api.model
    def _create_payment_transaction(self, order, **kwargs):
        """Intercept before payment transaction is created."""
        provider_id = int(kwargs.get('payment_provider_id') or 0)
        if provider_id:
            provider = self.env['payment.provider'].browse(provider_id)
            if provider and provider.code == 'authorize':
                fee_product = self.env['product.product'].search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)
                if fee_product:
                    # Remove old fee lines to avoid duplicates
                    order.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()

                    # Calculate fee (3.5% of untaxed amount)
                    fee = round(order.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })

        # Now proceed with normal transaction creation
        return super()._create_payment_transaction(order, **kwargs)
