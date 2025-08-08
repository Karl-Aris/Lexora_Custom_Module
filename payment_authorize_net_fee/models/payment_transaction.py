from odoo import models, fields, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    surcharge_accepted = fields.Boolean(string="Surcharge Accepted", default=False)
    surcharge_amount = fields.Monetary(string="Authorize.Net Surcharge", compute='_compute_surcharge_amount')

    @api.depends('amount', 'provider_code')
    def _compute_surcharge_amount(self):
        for tx in self:
            if tx.provider_code == 'authorize':
                tx.surcharge_amount = tx.amount * 0.035
            else:
                tx.surcharge_amount = 0.0
