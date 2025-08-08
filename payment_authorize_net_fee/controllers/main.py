# controllers/main.py

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class AuthorizeNetSurchargeController(http.Controller):

    @http.route(['/payment/authorize_net/start'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def authorize_net_start(self, **post):
        tx_id = post.get('transaction_id')
        if not tx_id:
            return request.redirect('/shop')

        try:
            tx = request.env['payment.transaction'].sudo().browse(int(tx_id))
        except (ValueError, TypeError):
            return request.redirect('/shop')

        if not tx.exists():
            return request.redirect('/shop')

        if tx.provider_code != 'authorize':
            # For other providers, proceed normally
            return request.redirect(tx.payment_url)

        # Redirect to surcharge confirmation page for Authorize.Net
        return request.redirect(f'/payment/authorize_net/surcharge?transaction_id={tx.id}')

    @http.route(['/payment/authorize_net/surcharge'], type='http', auth='public', website=True)
    def surcharge_page(self, transaction_id=None, **kwargs):
        try:
            tx = request.env['payment.transaction'].sudo().browse(int(transaction_id)) if transaction_id else None
        except (ValueError, TypeError):
            return request.redirect('/shop')

        if not tx or not tx.exists():
            return request.redirect('/shop')

        if tx.provider_code != 'authorize':
            return request.redirect(tx.payment_url)

        warning = request.session.pop('surcharge_warning', False)
        return request.render('payment_authorize_net_fee.surcharge_confirmation_template', {
            'transaction': tx,
            'warning': warning,
        })

    @http.route(['/payment/authorize_net/surcharge_confirm'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def surcharge_confirm(self, **post):
        tx_id = post.get('transaction_id')
        surcharge_accepted = post.get('surcharge_accept') == 'on'

        if not tx_id:
            return request.redirect('/shop')

        try:
            tx = request.env['payment.transaction'].sudo().browse(int(tx_id))
        except (ValueError, TypeError):
            return request.redirect('/shop')

        if not tx.exists():
            return request.redirect('/shop')

        if not surcharge_accepted:
            request.session['surcharge_warning'] = "You must accept the surcharge to continue payment."
            return request.redirect(f'/payment/authorize_net/surcharge?transaction_id={tx.id}')

        # Mark surcharge accepted
        tx.sudo().write({'surcharge_accepted': True})

        # Proceed with the actual payment redirect URL
        return request.redirect(tx.payment_url)
