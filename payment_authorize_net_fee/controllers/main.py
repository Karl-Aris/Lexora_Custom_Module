from odoo import http
from odoo.http import request

class AuthorizeNetFeeController(http.Controller):

    @http.route(['/authorize_net/add_fee'], type='json', auth='public', website=True, csrf=False)
    def add_fee(self, sale_order_id):
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        if not order:
            return {'error': 'Order not found'}

        # Find the fee product
        fee_product = request.env['product.product'].sudo().search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return {'error': 'Fee product not found'}

        # Remove existing fee line if already added
        order.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

        # Calculate fee as 3.5% of untaxed amount
        fee_amount = round(order.amount_untaxed * 0.035, 2)

        # Add fee line
        order.write({
            'order_line': [(0, 0, {
                'product_id': fee_product.id,
                'name': fee_product.name,
                'product_uom_qty': 1,
                'price_unit': fee_amount,
            })]
        })

        return {
            'success': True,
            'new_total': order.amount_total
        }
