# controllers/main.py
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleAuthorizeFee(WebsiteSale):

    def _create_payment_transaction(self, order, **kwargs):
        """Intercept before payment transaction is created."""
        provider_id = int(kwargs.get('payment_provider_id') or 0)
        if provider_id:
            provider = request.env['payment.provider'].browse(provider_id)
            if provider and provider.code == 'authorize':
                fee_product = request.env['product.product'].search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)
                if fee_product:
                    # Remove any previous fee line
                    order.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()

                    # Calculate fee
                    fee = round(order.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        request.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })

        return super()._create_payment_transaction(order, **kwargs)
