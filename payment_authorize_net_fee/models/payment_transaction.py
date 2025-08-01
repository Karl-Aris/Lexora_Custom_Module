from odoo import models, api, fields

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            provider_code = vals.get("provider_code")
            amount = vals.get("amount")
            if provider_code == "authorize_net" and amount:
                surcharge = round(amount * 0.035, 2)
                vals["amount"] = round(amount + surcharge, 2)
        return super().create(vals_list)
