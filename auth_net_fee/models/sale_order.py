from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _ensure_authorize_fee(self, provider_id):
        """
        Helper: add the surcharge line if provider is Authorize.Net.
        Returns True if fee was added/changed.
        """
        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            return False

        provider = self.env['payment.provider'].browse(provider_id) if provider_id else False
        if not provider or provider.code != 'authorize':
            # ensure we remove existing fee lines if provider not authorize
            self.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()
            return False

        # Skip if there is already a confirmed transaction
        has_confirmed_tx = self.transaction_ids.filtered(lambda t: t.state in ('done', 'authorized'))
        if has_confirmed_tx:
            return False

        # Remove old fee lines first (prevent duplicates)
        self.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()

        fee = round(self.amount_untaxed * 0.035, 2)
        if fee > 0:
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': fee_product.id,
                'name': fee_product.name,
                'price_unit': fee,
                'product_uom_qty': 1,
            })
            return True
        return False

    def _create_payment_transaction(self, vals):
        """
        This method is commonly used by some payment flows to create the transaction.
        Ensure surcharge is present before the transaction is created.
        """
        provider_id = vals.get('provider_id') or vals.get('provider')
        try:
            # If provider is present: ensure fee is created first on this SO
            if provider_id:
                # provider_id might be an int or a record id
                self._ensure_authorize_fee(provider_id)
        except Exception:
            # never break the flow; let transaction creation proceed
            pass
        return super()._create_payment_transaction(vals)
