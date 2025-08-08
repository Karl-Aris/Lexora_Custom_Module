from odoo import http
from odoo.http import request
import logging
from odoo.addons.website_sale.controllers import main as website_sale_main

_logger = logging.getLogger('payment_authorize_net_full.controller')

class WebsiteSaleAuthorizePrePayment(website_sale_main.WebsiteSale):
    """
    Controller-level pre-payment injection to ensure fee is applied before transaction creation.
    """

    def _inject_fee_for_order(self, order, provider_id):
        try:
            if not order or not provider_id:
                return False
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if not provider or (provider.code or '').lower() != 'authorize':
                return False

            fee_product = request.env['product.product'].sudo().search([('default_code','=', 'AUTH_NET_FEE')], limit=1)
            if not fee_product:
                _logger.info('payment_authorize_net_full: AUTH_NET_FEE product not found; skipping injection.')
                return False

            # skip if order already has confirmed tx
            confirmed = order.transaction_ids.filtered(lambda t: t.state in ('done', 'authorized'))
            if confirmed:
                _logger.info('payment_authorize_net_full: order %s already has confirmed tx; skipping injection.', order.name)
                return False

            # remove existing fee lines (prevent duplicates)
            order.order_line.filtered(lambda l: l.product_id.id == fee_product.id).sudo().unlink()

            fee = round(order.amount_untaxed * 0.035, 2)
            if fee <= 0:
                _logger.info('payment_authorize_net_full: computed fee 0 for order %s; skipping.', order.name)
                return False

            request.env['sale.order.line'].sudo().create({
                'order_id': order.id,
                'product_id': fee_product.id,
                'name': fee_product.name,
                'price_unit': fee,
                'product_uom_qty': 1,
            })
            _logger.info('payment_authorize_net_full: injected fee %s into order %s', fee, order.name)
            return True
        except Exception:
            _logger.exception('payment_authorize_net_full: error while injecting fee')
            return False

    @http.route(['/shop/payment', '/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def payment_transaction(self, **post):
        """
        Try to inject fee when portal payment flow submits. We attempt both endpoints
        to be robust against themes/versions.
        """
        try:
            order = request.website.sale_get_order()
            provider_id = post.get('provider_id') or post.get('acquirer_id') or post.get('provider') or post.get('acquirer') or post.get('payment_method_id')
            if order and provider_id:
                injected = self._inject_fee_for_order(order, provider_id)
                if injected:
                    # recompute totals
                    order.sudo()._amount_all()
                    request.env.cr.commit()
        except Exception:
            _logger.exception('payment_authorize_net_full: error in controller hook')
        # call super to let normal flow continue
        # WebsiteSale.payment_transaction exists in many setups; if not, fallback to parent method via super()
        return super(WebsiteSaleAuthorizePrePayment, self).payment_transaction(**post)
