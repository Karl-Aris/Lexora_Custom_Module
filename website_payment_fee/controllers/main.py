from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsitePaymentFee(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def shop_payment(self, **post):
        response = super().shop_payment(**post)
        order = request.website.sale_get_order()
        provider = post.get('provider')

        if order and provider:
            order.sudo().write({'x_payment_provider_code': provider})

            if provider == "authorize":
                product = request.env['product.product'].sudo().search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)

                if product:
                    # Avoid duplicate fee line
                    if not any(line.product_id.id == product.id for line in order.order_line):
                        order.sudo().order_line.create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'name': product.name,
                            'product_uom_qty': 1,
                            'product_uom': product.uom_id.id,
                            'price_unit': product.lst_price,
                        })

        return response
