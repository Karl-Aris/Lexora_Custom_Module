from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Override to add surcharge before rendering payment page. """
        order = request.website.sale_get_order()
        if order and order.payment_provider_id.code == 'authorize':
            fee_product = request.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
            if fee_product:
                existing_fee = order.order_line.filtered(lambda l: l.product_id.id == fee_product.id)
                if not existing_fee:
                    order._create_auth_net_fee_line(fee_product)
        return super().shop_payment(**post)

    @http.route(['/shop/payment/transaction'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_transaction(self, **post):
        """ Override to show thank you only after payment is done, not just payment method selection. """
        tx = request.env['payment.transaction'].sudo().browse(int(post.get('transaction_id', 0)))
        if tx and tx.state == 'done':
            return request.redirect('/shop/confirmation')
        else:
            return request.redirect('/shop/payment')
