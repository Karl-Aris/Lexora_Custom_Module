from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/payment/transaction'], type='http', auth="public", website=True, sitemap=False)
    def website_payment_transaction(self, **post):
        response = super().website_payment_transaction(**post)
        order = request.website.sale_get_order()
        if not order:
            return response

        provider = order.payment_provider_id
        if provider and provider.code == 'authorize_net':
            fee_product = request.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
            if fee_product:
                # Remove existing fee lines
                order.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

                fee_percent = provider.authnet_fee_percent or 0.0
                if fee_percent > 0:
                    fee_amount = order.amount_total * (fee_percent / 100.0)
                    order.order_line.create({
                        'order_id': order.id,
                        'product_id': fee_product.id,
                        'name': fee_product.name,
                        'product_uom_qty': 1,
                        'price_unit': fee_amount,
                    })

        return response
