
from odoo import http
from odoo.http import request

class WebsiteSaleAuthorizeFee(http.Controller):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, csrf=False)
    def payment(self, **post):
        response = request.website.sale_payment(**post)
        order = request.website.sale_get_order()
        acquirer_id = int(post.get('acquirer_id', 0))
        acquirer = request.env['payment.acquirer'].sudo().browse(acquirer_id)
        fee_product = request.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

        if order and acquirer.provider == 'authorize' and fee_product:
            existing_fee_line = order.order_line.filtered(lambda l: l.product_id == fee_product)
            fee = order.amount_untaxed * 0.035

            if existing_fee_line:
                existing_fee_line.write({'price_unit': round(fee, 2)})
            else:
                request.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': fee_product.id,
                    'name': fee_product.name,
                    'product_uom_qty': 1,
                    'price_unit': round(fee, 2),
                    'order_partner_id': order.partner_id.id,
                })

        return response
