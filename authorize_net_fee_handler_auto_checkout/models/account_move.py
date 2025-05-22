from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _add_authorize_net_fee_line_if_needed(self, payment):
        # Only add the fee if payment method is Authorize.Net
        if payment.payment_method_id.code != 'authorize':
            return

        # Avoid duplicate fee lines
        fee_product = self.env.ref('authorize_net_fee_handler_auto_checkout.product_authorize_net_fee')
        for line in self.invoice_line_ids:
            if line.product_id == fee_product:
                return  # already added

        fee_amount = self.amount_total * 0.03

        self.invoice_line_ids.create({
            'move_id': self.id,
            'product_id': fee_product.id,
            'name': 'Authorize.Net Surcharge (3%)',
            'quantity': 1,
            'price_unit': fee_amount,
            'account_id': fee_product.property_account_income_id.id or fee_product.categ_id.property_account_income_categ_id.id,
        })
