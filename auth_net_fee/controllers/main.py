from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAuthorizeFee(WebsiteSale):
    @http.route(['/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def payment_transaction(self, **post):
        """
        Controller-level injection: when the portal payment form is submitted,
        check the chosen provider_id and — if it's Authorize.Net — inject the fee
        into the current sale order _before_ super() handles payment transaction creation.
        """
        try:
            sale_order = request.website.sale_get_order()
            provider_id = post.get('provider_id') or post.get('provider')  # handle different param names
            if sale_order and provider_id:
                provider = request.env['payment.provider'].browse(int(provider_id))
                if provider and provider.code == 'authorize':
                    # find the fee product
                    fee_product = request.env['product.product'].sudo().search([
                        ('default_code', '=', 'AUTH_NET_FEE')
                    ], limit=1)
                    if fee_product:
                        # Skip if there's already a confirmed transaction for this order
                        has_confirmed_tx = sale_order.transaction_ids.filtered(
                            lambda t: t.state in ('done', 'authorized')
                        )
                        if not has_confirmed_tx:
                            # Remove any old fee lines (prevent duplicates)
                            sale_order.order_line.filtered(
                                lambda l: l.product_id.id == fee_product.id
                            ).sudo().unlink()

                            # Add fee line
                            fee = round(sale_order.amount_untaxed * 0.035, 2)
                            if fee > 0:
                                request.env['sale.order.line'].sudo().create({
                                    'order_id': sale_order.id,
                                    'product_id': fee_product.id,
                                    'name': fee_product.name,
                                    'price_unit': fee,
                                    'product_uom_qty': 1,
                                })
        except Exception:
            # Don't break the flow — if anything fails here, fallback hooks will try later.
            request.env.cr.rollback()
        # Continue with the standard flow (this will create the transaction using the updated SO)
        return super().payment_transaction(**post)
