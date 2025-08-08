from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _extract_so_ids_from_vals(self, sale_order_ids):
        """
        Handles different structures for sale_order_ids in create vals.
        Examples:
          - [(6, 0, [so_id])]
          - [(4, so_id), ...]
        Returns list of ids.
        """
        ids = []
        if not sale_order_ids:
            return ids
        # typical many2many (6, 0, [ids])
        if isinstance(sale_order_ids, list):
            for item in sale_order_ids:
                if isinstance(item, (list, tuple)) and len(item) >= 3 and item[0] == 6:
                    ids.extend(item[2] or [])
                elif isinstance(item, (list, tuple)) and len(item) >= 2 and item[0] == 4:
                    # (4, id)
                    ids.append(item[1])
        elif isinstance(sale_order_ids, (int,)):
            ids = [sale_order_ids]
        return ids

    @api.model_create_multi
    def create(self, vals_list):
        """
        Fallback: ensure fee is present BEFORE calling super().create()
        in case any flow bypassed the controller or sale order hook.
        """
        SaleOrder = self.env['sale.order']
        Product = self.env['product.product']
        Provider = self.env['payment.provider']

        # Pre-fetch fee product
        fee_product = Product.search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        for vals in vals_list:
            try:
                sale_order_ids_val = vals.get('sale_order_ids')
                so_ids = self._extract_so_ids_from_vals(sale_order_ids_val)
                if not so_ids:
                    continue
                sale_orders = SaleOrder.browse(so_ids)
                if not fee_product:
                    continue
                # determine provider id from vals or fall back to first SO's payment_provider_id
                provider_id = vals.get('provider_id')
                if not provider_id:
                    provider_id = sale_orders and sale_orders[0].payment_provider_id.id or None

                if not provider_id:
                    continue

                provider = Provider.browse(provider_id)
                if provider and provider.code == 'authorize':
                    for so in sale_orders:
                        # Skip if a confirmed transaction already exists
                        if so.transaction_ids.filtered(lambda t: t.state in ('done', 'authorized')):
                            continue
                        # remove existing fee lines
                        so.order_line.filtered(lambda l: l.product_id.id == fee_product.id).unlink()
                        fee = round(so.amount_untaxed * 0.035, 2)
                        if fee > 0:
                            # create the fee line on the SO
                            self.env['sale.order.line'].create({
                                'order_id': so.id,
                                'product_id': fee_product.id,
                                'name': fee_product.name,
                                'price_unit': fee,
                                'product_uom_qty': 1,
                            })
            except Exception:
                # swallow exceptions so we do not break transaction creation;
                # the controller or sale_order hook should have already tried.
                continue

        # now proceed to create transactions (with the SO totals updated)
        return super().create(vals_list)
