from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_sale_order_from_vendor_bill()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_sale_order_from_vendor_bill()
        return res

    def _update_sale_order_from_vendor_bill(self):
        for rec in self:
            if rec.move_type == 'in_invoice' and rec.sale_order_id:
                # get all related vendor bills for the sale order
                related_moves = self.search([
                    ('sale_order_id', '=', rec.sale_order_id.id),
                    ('move_type', '=', 'in_invoice'),
                    ('name', '!=', '/')
                ])

                # collect all bill names
                vb_numbers = ', '.join(related_moves.mapped('name'))
                # sum all amounts
                total_amount = sum(related_moves.mapped('amount_total_signed'))
                # collect all invoice dates as strings
                vb_dates = ', '.join(
                    [d.strftime('%Y-%m-%d') for d in related_moves.mapped('invoice_date') if d]
                )

                vals = {
                    'x_vb_number': vb_numbers,
                    'x_amount': total_amount,       # sum of all bills
                    'x_bol': rec.ref,               # last bill ref
                    'x_vb_date_char': vb_dates,     # all vendor bill dates
                }
                if rec.invoice_date:
                    vals['x_vb_date'] = rec.invoice_date  # still keep latest date in x_vb_date
                rec.sale_order_id.write(vals)
