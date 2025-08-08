from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _apply_authorize_fee(self):
        """Add 3.5% surcharge to related sale orders for Authorize.Net and sync transaction amount."""
        fee_product = self.env['product.product'].search([
            ('default_code', '=', 'AUTH_NET_FEE')
        ], limit=1)

        for tx in self:
            if (
                tx.provider_id.code == 'authorize'
                and tx.sale_order_ids
                and fee_product
            ):
                for so in tx.sale_order_ids:
                    # Remove previous surcharge lines
                    so.order_line.filtered(
                        lambda l: l.product_id.id == fee_product.id
                    ).unlink()

                    # Calculate and add fee
                    fee = round(so.amount_untaxed * 0.035, 2)
                    if fee > 0:
                        self.env['sale.order.line'].create({
                            'order_id': so.id,
                            'product_id': fee_product.id,
                            'name': fee_product.name,
                            'price_unit': fee,
                            'product_uom_qty': 1,
                        })

                # After adding fee, ensure transaction amount matches SO total
                if len(tx.sale_order_ids) == 1:
                    tx.amount = tx.sale_order_ids.amount_total
                elif tx.sale_order_ids:
                    tx.amount = sum(so.amount_total for so in tx.sale_order_ids)

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)
        transactions._apply_authorize_fee()
        return transactions

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ['sale_order_ids', 'provider_id']):
            self._apply_authorize_fee()
        return res
