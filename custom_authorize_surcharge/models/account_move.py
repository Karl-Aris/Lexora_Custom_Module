from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)

        try:
            if move.move_type == 'out_invoice' and move.payment_reference:
                surcharge_product = self.env.ref('custom_authorize_surcharge.authorize_surcharge_product_id')

                if not any(line.product_id == surcharge_product for line in move.invoice_line_ids):
                    surcharge_amount = round(move.amount_untaxed * 0.03, 2)
                    account_id = (
                        move.invoice_line_ids[:1].account_id.id or
                        surcharge_product.categ_id.property_account_income_categ_id.id
                    )

                    if account_id:
                        move.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': surcharge_product.id,
                                'quantity': 1,
                                'price_unit': surcharge_amount,
                                'name': 'Authorize.Net Surcharge',
                                'account_id': account_id,
                            })]
                        })
                        move._recompute_tax_lines()
        except Exception as e:
            _logger.error("Failed to add surcharge: %s", str(e))

        return move
