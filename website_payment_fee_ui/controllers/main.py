from odoo import http
from odoo.http import request

class PaymentFeeController(http.Controller):
    @http.route('/get_payment_fee', type='json', auth='public', website=True)
    def get_payment_fee(self, provider_id):
        provider = request.env['payment.provider'].sudo().browse(int(provider_id))
        order = request.website.sale_get_order()
        amount = order.amount_total if order else 0
        fee = amount * (provider.fee_percent / 100.0)
        return {"fee": fee}