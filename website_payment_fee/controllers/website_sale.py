from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route

class WebsiteSaleInherit(WebsiteSale):

    @route(['/shop/payment/transaction'], type='http', auth="public", website=True, csrf=False)
    def payment_transaction(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop')

        provider_id = int(post.get('provider_id', 0))
        provider = request.env['payment.provider'].sudo().browse(provider_id)

        # Store provider name if needed (optional field on SO)
        order.sudo().write({'x_payment_method': provider.name})

        # Add Fee Product
        fee_product = request.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if fee_product:
            existing_fee = order.order_line.filtered(lambda l: l.product_id == fee_product)
            if not existing_fee:
                fee = provider.fixed_fee or 0.0
                if provider.percentage_fee:
                    fee += (order.amount_total * provider.percentage_fee) / 100
                request.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': 'Payment Processing Fee',
                    'price_unit': fee,
                    'product_uom_qty': 1,
                })

        return super().payment_transaction(**post)