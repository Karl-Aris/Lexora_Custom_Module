from odoo import models

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        payments = super()._create_payments()

        for payment in payments:
            if payment.payment_method_line_id and payment.payment_method_line_id.payment_provider_id.code == 'authorize':
                for invoice in payment.reconciled_invoices:
                    invoice.apply_authorize_net_fee(payment.transaction_id or payment)

        return payments
