from odoo import models, api, exceptions

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        #move = super().create(vals)

        if move.move_type == 'out_invoice' and move.payment_reference:
            try:
                surcharge_product = self.env.ref('custom_authorize_surcharge.authorize_surcharge_product_id')
            except Exception:
                raise exceptions.UserError("Missing 'Authorize.Net Surcharge' product configuration.")

            if not any(line.product_id == surcharge_product for line in move.invoice_line_ids):
                surcharge_amount = round(move.amount_untaxed * 0.03, 2)

                # Get account_id safely
                account_id = (
                    move.invoice_line_ids[:1].account_id.id or
                    surcharge_product.categ_id.property_account_income_categ_id.id
                )

                if not account_id:
                    raise exceptions.UserError("Missing income account on product or invoice lines.")

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

        return move
