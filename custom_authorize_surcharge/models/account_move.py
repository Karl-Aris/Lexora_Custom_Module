from odoo import models, api, exceptions
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)
        try:
            if move.move_type == 'out_invoice' and move.payment_reference:
                surcharge_product = self.env['product.product'].search(
                    [('default_code', '=', 'authorize_surcharge')], limit=1
                )
                if not surcharge_product:
                    raise exceptions.UserError("Surcharge product with internal reference 'authorize_surcharge' not found.")

                if not any(line.product_id == surcharge_product for line in move.invoice_line_ids):
                    surcharge_amount = round(move.amount_untaxed * 0.03, 2)

                    account_id = (
                        move.invoice_line_ids[:1].account_id.id if move.invoice_line_ids else False
                    ) or surcharge_product.categ_id.property_account_income_categ_id.id

                    if not account_id:
                        raise exceptions.UserError("No income account defined on surcharge product or invoice lines.")

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
            _logger.error("Error in surcharge create method: %s", e)
            # Optionally re-raise or just continue:
            # raise

        return move
