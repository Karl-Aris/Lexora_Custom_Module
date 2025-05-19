from odoo import models, api, exceptions
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)
        try:
            # Only proceed for customer invoices
            if move.move_type == 'out_invoice' and move.payment_reference:
                # Find surcharge product by default_code
                surcharge_product = self.env['product.product'].search(
                    [('default_code', '=', 'authorize_surcharge')], limit=1
                )
                if not surcharge_product:
                    raise exceptions.UserError(
                        "Surcharge product with internal reference 'authorize_surcharge' not found."
                    )
                
                # Check if surcharge line already exists to avoid duplicates
                surcharge_line_exists = any(
                    line.product_id == surcharge_product for line in move.invoice_line_ids
                )
                if not surcharge_line_exists:
                    # Calculate surcharge amount as 3% of untaxed amount
                    surcharge_amount = round(move.amount_untaxed * 0.03, 2)
                    if surcharge_amount <= 0:
                        _logger.info("Surcharge amount is 0 or less, skipping surcharge line.")
                        return move
                    
                    # Determine the income account for surcharge line
                    account_id = (
                        move.invoice_line_ids[:1].account_id.id if move.invoice_line_ids else False
                    ) or surcharge_product.categ_id.property_account_income_categ_id.id
                    
                    if not account_id:
                        raise exceptions.UserError(
                            "No income account defined on surcharge product or invoice lines."
                        )
                    
                    # Add surcharge invoice line
                    move.write({
                        'invoice_line_ids': [(0, 0, {
                            'product_id': surcharge_product.id,
                            'quantity': 1,
                            'price_unit': surcharge_amount,
                            'name': 'Authorize.Net Surcharge',
                            'account_id': account_id,
                        })]
                    })
                    # Recompute taxes
                    move._recompute_tax_lines()
                    _logger.info("Authorize.Net surcharge line added with amount %s", surcharge_amount)
        
        except Exception as e:
            _logger.error("Error adding surcharge line: %s", e)
            # Optionally raise or silently continue

        return move
