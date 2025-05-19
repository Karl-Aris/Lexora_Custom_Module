from odoo import models, api, exceptions

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)

        # Only add surcharge to customer invoices with a payment reference
        if move.move_type == 'out_invoice' and move.payment_reference:
            try:
                surcharge_product = self.env.ref('your_module_name.authorize_surcharge_product_id')
            except exceptions.MissingError:
                raise exceptions.UserError("Surcharge product not found. Please configure 'authorize_surcharge_product_id' properly.")

            # Check if the surcharge is already applied
            if surcharge_product and not any(line.product_id == surcharge_product for line in move.invoice_line_ids):
                surcharge_amount = move.amount_untaxed * 0.03

                # Use the account from an existing line if available, else fallback
                account_id = move.invoice_line_ids[:1].account_id.id or surcharge_product.categ_id.property_account_income_categ_id.id

                move.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': surcharge_product.id,
                        'quantity': 1,
                        'price_unit': surcharge_amount,
                        'name': 'Authorize.Net Surcharge',
                        'account_id': account_id,
                    })]
                })
        return move
