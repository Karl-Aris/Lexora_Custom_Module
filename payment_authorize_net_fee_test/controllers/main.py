from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAuthorizeFee(WebsiteSale):

    @http.route(['/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def payment_transaction(self, **post):
        sale_order = request.website.sale_get_order()
        if sale_order and post.get('provider_id'):
            provider = request.env['payment.provider'].browse(int(post['provider_id']))
            if provider.code == 'authorize':
                fee_product = request.env['product.product'].search([
                    ('default_code', '=', 'AUTH_NET_FEE')
                ], limit=1)
                if fee_product:
                    # Remove old fee lines
                    sale_order.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()
                    # Add new fee
                    fee = round(sale_order.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        request.env['sale.order.line'].sudo().create({
                            'order_id': sale_order.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })
        return super().payment_transaction(**post)
