from odoo import http
from odoo.http import request

class PaymentFeeController(http.Controller):

    @http.route(['/payment/get_fee'], type='json', auth='public', website=True)
    def get_fee(self, provider_id):
        order = request.website.sale_get_order()
        provider = request.env['payment.provider'].sudo().browse(int(provider_id))

        fee = provider.fixed_fee or 0.0
        if provider.percentage_fee:
            fee += (order.amount_total * provider.percentage_fee) / 100

        return {
            'fee_amount': fee,
            'fee_display': "+ $%.2f Fees" % fee
        }