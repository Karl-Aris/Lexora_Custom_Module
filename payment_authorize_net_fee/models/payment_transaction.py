import logging
from odoo import models, api

_logger = logging.getLogger('payment_authorize_net_fee')

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _parse_sale_order_ids_vals(self, sale_order_ids):
        """Return list of ids from common many2many commands in create vals."""
        ids = []
        if not sale_order_ids:
            return ids
        if isinstance(sale_order_ids, list):
            for item in sale_order_ids:
                if isinstance(item, (list, tuple)):
                    if item and item[0] == 6 and len(item) >= 3:
                        ids.extend(item[2] or [])
                    elif item and item[0] == 4 and len(item) >= 2:
                        ids.append(item[1])
                elif isinstance(item, int):
                    ids.append(item)
        elif isinstance(sale_order_ids, int):
            ids.append(sale_order_ids)
        return list(set(ids))

    def _is_authorize_provider(self, provider):
        """Flexible detection for Authorize.Net providers."""
        if not provider:
            return False
        code = (provider.code or '').lower()
        name = (getattr(provider, 'name', '') or '').lower()
        # catch common variations — adjust if your provider has a custom code
        return ('authoriz' in code) or ('authoriz' in name) or code in ('authorize', 'authorize_net', 'authorizenet')

    @api.model_create_multi
    def create(self, vals_list):
        """
        Pre-create hook: before transaction records are actually created, ensure
        that if the provider is Authorize.Net and there are sale orders linked,
        the AUTH_NET_FEE line is present on those sale orders and `vals['amount']`
        is set to the updated SO total.
        """
        Product = self.env['product.product']
        SaleOrder = self.env['sale.order']
        Provider = self.env['payment.provider']

        fee_product = Product.search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

        for vals in vals_list:
            try:
                # Detect provider id from many possible keys
                provider_id = vals.get('provider_id') or vals.get('provider') or vals.get('acquirer_id') or vals.get('payment_provider_id')

                # Extract sale order ids from many2many commands if present
                so_ids = []
                if vals.get('sale_order_ids'):
                    so_ids = self._parse_sale_order_ids_vals(vals.get('sale_order_ids'))
                elif vals.get('sale_order_id'):
                    so_ids = [vals.get('sale_order_id')]

                if not so_ids:
                    # nothing to do for this transaction
                    continue

                # Determine provider (fall back to first SO payment provider if missing)
                provider = Provider.browse(provider_id) if provider_id else None
                if not provider:
                    so0 = SaleOrder.browse(so_ids[0])
                    provider = so0.payment_provider_id or None

                if not provider or not self._is_authorize_provider(provider):
                    continue

                if not fee_product:
                    _logger.info('payment_authorize_net_fee: AUTH_NET_FEE product not found; skipping surcharge injection.')
                    continue

                # Operate with sudo on SO lines to avoid access issues from portal user
                sale_orders = SaleOrder.browse(so_ids).sudo()

                for so in sale_orders:
                    # If order already has a confirmed/authorized tx => DO NOT inject (prevents duplicates)
                    if so.transaction_ids.filtered(lambda t: t.state in ('done', 'authorized')):
                        _logger.info('payment_authorize_net_fee: skipping injection for %s — it already has confirmed transaction(s).', so.name)
                        continue

                    # Remove existing fee lines to avoid duplicates
                    existing_lines = so.order_line.filtered(lambda l: l.product_id.id == fee_product.id)
                    if existing_lines:
                        existing_lines.sudo().unlink()

                    # Calculate fee (based on amount_untaxed, as requested)
                    fee = round(so.amount_untaxed * 0.035, 2)
                    if fee <= 0:
                        _logger.info('payment_authorize_net_fee: computed fee 0 for %s; skipping.', so.name)
                        continue

                    # Create fee line
                    self.env['sale.order.line'].sudo().create({
                        'order_id': so.id,
                        'product_id': fee_product.id,
                        'name': fee_product.name,
                        'price_unit': fee,
                        'product_uom_qty': 1,
                    })

                    # Recompute totals on the SO
                    so.sudo()._amount_all()
                    _logger.info('payment_authorize_net_fee: injected fee %s on order %s', fee, so.name)

                # Update transaction amount to reflect new SO totals
                total_amount = sum(SaleOrder.browse(so_ids).mapped('amount_total'))
                vals['amount'] = float(total_amount)
                _logger.info('payment_authorize_net_fee: set transaction amount=%s for SO ids=%s', vals['amount'], so_ids)

            except Exception:
                _logger.exception('payment_authorize_net_fee: error during pre-create injection')

        # Now create transactions with potentially-updated vals (amount matching SO totals)
        return super(PaymentTransaction, self).create(vals_list)

    def write(self, vals):
        """
        Fallback: if sale_order_ids or provider changed later via write, try to apply the fee.
        This is a best-effort fallback; the create() hook is the main mechanism.
        """
        res = super(PaymentTransaction, self).write(vals)

        # Only attempt fallback if relevant fields were changed
        if any(k in vals for k in ('sale_order_ids', 'sale_order_id', 'provider_id', 'provider', 'acquirer_id', 'payment_provider_id')):
            Product = self.env['product.product']
            fee_product = Product.search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)

            for tx in self:
                try:
                    provider = tx.provider_id or tx.acquirer_id or tx.payment_provider_id
                    if not provider or not self._is_authorize_provider(provider):
                        continue
                    if not tx.sale_order_ids:
                        continue
                    if not fee_product:
                        _logger.info('payment_authorize_net_fee: AUTH_NET_FEE missing in write fallback; skipping.')
                        continue

                    for so in tx.sale_order_ids.sudo():
                        # If there's a confirmed transaction for this order that is not this tx -> skip injecting to avoid duplicate pay
                        if so.transaction_ids.filtered(lambda t: t.state in ('done', 'authorized') and t.id != tx.id):
                            _logger.info('payment_authorize_net_fee: order %s already has other confirmed tx; skipping fallback injection.', so.name)
                            continue

                        # Remove existing fee lines
                        existing_lines = so.order_line.filtered(lambda l: l.product_id.id == fee_product.id)
                        if existing_lines:
                            existing_lines.sudo().unlink()

                        fee = round(so.amount_untaxed * 0.035, 2)
                        if fee <= 0:
                            continue

                        self.env['sale.order.line'].sudo().create({
                            'order_id': so.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })
                        so.sudo()._amount_all()
                        _logger.info('payment_authorize_net_fee: fallback injected fee %s on order %s for tx %s', fee, so.name, tx.reference or tx.id)

                    # Keep transaction amount in sync
                    new_amount = sum(so.amount_total for so in tx.sale_order_ids)
                    # Only update if different (avoid unnecessary writes)
                    if float(tx.amount) != float(new_amount):
                        tx.amount = new_amount
                        _logger.info('payment_authorize_net_fee: updated tx %s amount to %s', tx.reference or tx.id, new_amount)

                except Exception:
                    _logger.exception('payment_authorize_net_fee: error in write fallback')

        return res
