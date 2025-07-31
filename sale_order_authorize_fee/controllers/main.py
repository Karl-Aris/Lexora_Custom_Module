from odoo import http
from odoo.http import request

class PaymentFeeController(http.Controller):

    @http.route(['/payment/pay'], type='http', auth="public", website=True, csrf=False)
    def custom_payment_fee_handler(self, **post):
        sale_order = request.website.sale_get_order()
        acquirer_id = int(post.get('acquirer_id', 0))

        if not sale_order or not acquirer_id:
            return request.redirect('/shop/checkout')

        # Load the selected acquirer
        acquirer = request.env['payment.acquirer'].sudo().browse(acquirer_id)

        # Only apply fee for Authorize.Net
        if acquirer.provider == 'authorize_net':
            fee_product = request.env['product.product'].sudo().search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if fee_product:
                # Check if fee line is already there
                existing_line = sale_order.order_line.filtered(
                    lambda l: l.product_id.id == fee_product.id
                )

                if not existing_line:
                    fee = round(sale_order.amount_total * 0.035, 2)

                    sale_order.order_line.create({
                        'order_id': sale_order.id,
                        'product_id': fee_product.id,
                        'name': fee_product.name,
                        'price_unit': fee,
                        'product_uom_qty': 1,
                        'product_uom': fee_product.uom_id.id,
                    })

                    # Recompute totals
                    sale_order._amount_all()

        # Proceed to standard payment processing
        return request.redirect('/payment/process')
