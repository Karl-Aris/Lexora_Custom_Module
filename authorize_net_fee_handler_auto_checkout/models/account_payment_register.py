from odoo import models

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        payments = super()._create_payments()
        for payment in payments:
            for invoice in payment.reconciled_invoice_ids:
                invoice._add_authorize_net_fee_line_if_needed(payment)
        return payments
