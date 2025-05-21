from odoo import models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        payment = super().create(vals)
        self._apply_authorize_surcharge(payment)
        return payment

    def _apply_authorize_surcharge(self, payment):
        if not payment.payment_method_line_id or 'authorize' not in payment.payment_method_line_id.name.lower():
            return

        for invoice in payment.reconciled_invoice_ids:
            if any("Authorize.Net Surcharge" in l.name for l in invoice.invoice_line_ids):
                continue

            surcharge_amount = invoice.amount_total * 0.03
            product = self.env['product.product'].search([('name', '=', 'Authorize.Net Surcharge')], limit=1)

            if product and surcharge_amount > 0:
                invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': product.id,
                        'name': '3% Authorize.Net Surcharge',
                        'quantity': 1,
                        'price_unit': surcharge_amount,
                    })]
                })
