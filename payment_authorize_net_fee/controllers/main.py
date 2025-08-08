from odoo import http
from odoo.http import request

class AuthorizeNetSurchargeController(http.Controller):

    @http.route(['/payment/authorize_net/surcharge_confirm'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def surcharge_confirm(self, **post):
        tx_id = post.get('transaction_id')
        surcharge_accepted = post.get('surcharge_accept') == 'on'

        if not tx_id:
            return request.redirect('/shop')

        tx = request.env['payment.transaction'].sudo().browse(int(tx_id))
        if not tx.exists():
            return request.redirect('/shop')

        if not surcharge_accepted:
            # If surcharge not accepted, redirect back to payment page with warning
            request.session['surcharge_warning'] = "You must accept the surcharge to continue payment."
            return request.redirect(tx.payment_url)

        # Mark surcharge accepted
        tx.sudo().write({'surcharge_accepted': True})

        # Proceed with the payment (redirect to original payment url)
        return request.redirect(tx.payment_url)

    @http.route(['/payment/authorize_net/surcharge'], type='http', auth='public', website=True)
    def surcharge_page(self, transaction_id=None, **kwargs):
        tx = request.env['payment.transaction'].sudo().browse(int(transaction_id)) if transaction_id else None
        if not tx or not tx.exists():
            return request.redirect('/shop')

        # Show surcharge confirmation page only for authorize payment provider
        if tx.provider_code != 'authorize':
            return request.redirect(tx.payment_url)

        warning = request.session.pop('surcharge_warning', False)
        return request.render('payment_authorize_net_fee.surcharge_confirmation_template', {
            'transaction': tx,
            'warning': warning,
        })
