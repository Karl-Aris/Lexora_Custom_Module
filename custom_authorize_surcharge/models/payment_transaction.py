from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)

        # Only process customer invoices (not vendor bills, etc.)
        if move.move_type == 'out_invoice':
            try:
                # Reference your surcharge product
                surcharge_product = self.env.ref('custom_authorize_surcharge.authorize_surcharge_product_id')
                
                # Avoid double-adding
                already_has_surcharge = any(
                    line.product_id.id == surcharge_product.id for line in move.invoice_line_ids
                )

                if not already_has_surcharge:
                    # Calculate 3% of subtotal
                    surcharge_amount = move.amount_untaxed * 0.03

                    # Add the surcharge line
                    move.write({
                        'invoice_line_ids': [(0, 0, {
                            'product_id': surcharge_product.id,
                            'quantity': 1,
                            'price_unit': surcharge_amount,
                            'name': 'Authorize.Net Surcharge',
                            'account_id': move.invoice_line_ids[0].account_id.id if move.invoice_line_ids else self.env['account.account'].search([('user_type_id.type', '=', 'income')], limit=1).id,
                        })]
                    })
                    
        return move
