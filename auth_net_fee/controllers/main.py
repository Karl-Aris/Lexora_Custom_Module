from odoo import http
from odoo.http import request
import logging
from odoo.addons.website_sale.controllers import main as website_sale_main

_logger = logging.getLogger(__name__)

class WebsiteSaleAuthorizePrePayment(website_sale_main.WebsiteSale):
    """
    Override several portal entry points to ensure the Authorize.Net fee is injected
    into the sale order BEFORE a payment.transaction is created.
    This tries multiple commonly-used endpoints used by different configurations.
    """

    def _inject_fee_for_order(self, order, provider_id):
        try:
            if not order or not provider_id:
                return False
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if not provider or provider.code != 'authorize':
                return False

            fee_product = request.env['product.product'].sudo().search([('default_code','=', 'AUTH_NET_FEE')], limit=1)
            if not fee_product:
                _logger.info('AUTH_NET_FEE product not found; skipping injection.')
                return False

            # if there's already a confirmed transaction, skip injection to avoid duplicates
            confirmed = order.transaction_ids.filtered(lambda t: t.state in ('done','authorized'))
            if confirmed:
                _logger.info('Order %s already has confirmed transaction(s); skipping fee injection.' % order.name)
                return False

            # remove existing fee lines to prevent duplication
            order.order_line.filtered(lambda l: l.product_id.id == fee_product.id).sudo().unlink()

            fee = round(order.amount_untaxed * 0.035, 2)
            if fee <= 0:
                _logger.info('Computed fee is 0 for order %s; skipping.' % order.name)
                return False

            request.env['sale.order.line'].sudo().create({
                'order_id': order.id,
                'product_id': fee_product.id,
                'name': fee_product.name,
                'price_unit': fee,
                'product_uom_qty': 1,
            })
            _logger.info('Injected Authorize.Net fee (%s) into order %s' % (fee, order.name))
            return True
        except Exception as e:
            _logger.exception('Error injecting authorize fee: %s', e)
            return False

    @http.route(['/shop/payment'], type='http', auth='public', website=True, csrf=False)
    def payment(self, **post):
        """Override /shop/payment — often used when rendering the payment page (GET/POST)."""
        try:
            order = request.website.sale_get_order()
            provider_id = post.get('provider_id') or post.get('acquirer_id') or post.get('provider') or post.get('acquirer')
            if order and provider_id:
                self._inject_fee_for_order(order, provider_id)
        except Exception as e:
            _logger.exception('payment override error: %s', e)
        return super(WebsiteSaleAuthorizePrePayment, self).payment(**post)

    @http.route(['/shop/payment/transaction', '/shop/payment/transaction/'], type='http', auth='public', website=True, csrf=False)
    def payment_transaction(self, **post):
        """Override /shop/payment/transaction — this is the common submission endpoint."""
        try:
            order = request.website.sale_get_order()
            # try various param names that different themes or versions may use
            provider_id = post.get('provider_id') or post.get('acquirer_id') or post.get('provider') or post.get('acquirer') or post.get('payment_method_id')
            if order and provider_id:
                injected = self._inject_fee_for_order(order, provider_id)
                if injected:
                    # important: recompute order totals on the spot so the form reflects new amounts
                    order._amount_all()
                    request.env.cr.commit()  # persist changes before super() creates transactions
        except Exception as e:
            _logger.exception('payment_transaction override error: %s', e)
        return super(WebsiteSaleAuthorizePrePayment, self).payment_transaction(**post)

    @http.route(['/payment/transaction/process'], type='json', auth='public', website=True, csrf=False)
    def transaction_process_json(self, **post):
        """Some setups call JSON endpoints — intercept and inject fee too."""
        try:
            order = request.website.sale_get_order()
            provider_id = post.get('provider_id') or post.get('acquirer_id') or post.get('provider') or post.get('acquirer')
            if order and provider_id:
                self._inject_fee_for_order(order, provider_id)
                order._amount_all()
                request.env.cr.commit()
        except Exception as e:
            _logger.exception('transaction_process_json error: %s', e)
        # Not returning anything special — let caller proceed.
        return super(WebsiteSaleAuthorizePrePayment, self).transaction_process_json(**post) if hasattr(super(WebsiteSaleAuthorizePrePayment, self), 'transaction_process_json') else {}
