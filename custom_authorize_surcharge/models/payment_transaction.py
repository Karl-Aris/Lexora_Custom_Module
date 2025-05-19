from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)
        
        # Only add surcharge to customer invoices
        if move.move_type == 'out_invoice' and move.payment_reference:
            surcharge_product = self.env.ref('your_module_name.authorize_surcharge_product_id')  # Replace with actual external ID
            if not any(line.product_id == surcharge_product for line in move.invoice_line_ids):
                surcharge_amount = move.amount_untaxed * 0.03
                move.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': surcharge_product.id,
                        'quantity': 1,
                        'price_unit': surcharge_amount,
                        'name': 'Authorize.Net Surcharge',
                        'account_id': move.invoice_line_ids[0].account_id.id,  # Use the same income account
                    })]
                })
        return move
