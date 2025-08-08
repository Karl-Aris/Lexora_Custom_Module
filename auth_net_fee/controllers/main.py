from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAuthorizeNetFee(WebsiteSale):

    @http.route(['/shop/payment/transaction/'], type='http', auth="public", website=True, sitemap=False)
    def payment_transaction(self, **post):
        # Detect sale order
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop/cart')

        provider_id = int(post.get('provider_id', 0))
        if provider_id:
            provider = request.env['payment.provider'].sudo().browse(provider_id)
            if provider and provider.code == 'authorize':
                fee_product = request.env['product.product'].sudo().search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)
                if fee_product:
                    # Remove old fee lines
                    order.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()
                    # Calculate fee
                    fee = round(order.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        request.env['sale.order.line'].sudo().create({
                            'order_id': order.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })

        # Continue with original payment creation
        return super(WebsiteSaleAuthorizeNetFee, self).payment_transaction(**post)
