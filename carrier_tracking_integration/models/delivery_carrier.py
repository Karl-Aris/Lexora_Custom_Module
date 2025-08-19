from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_integration_enabled = fields.Boolean("Enable Tracking Integration")
    tracking_carrier = fields.Selection([
        ("ups", "UPS"),
        ("fedex", "FedEx"),
        ("dhl", "DHL"),
    ], string="Carrier")
    tracking_api_key = fields.Char("API Key")
    tracking_account_number = fields.Char("Account Number")

    def action_test_tracking_connection(self):
        for carrier in self:
            if not carrier.tracking_integration_enabled:
                raise UserError(_("Tracking integration is not enabled."))
            if not carrier.tracking_carrier:
                raise UserError(_("Please select a carrier."))
            if not carrier.tracking_api_key:
                raise UserError(_("Please provide API Key."))

            # Simulated test (you’d replace this with API calls per carrier)
            if carrier.tracking_carrier == "ups":
                msg = _("UPS test connection successful.")
            elif carrier.tracking_carrier == "fedex":
                msg = _("FedEx test connection successful.")
            elif carrier.tracking_carrier == "dhl":
                msg = _("DHL test connection successful.")
            else:
                msg = _("Unknown carrier.")

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": msg,
                    "type": "rainbow_man",
                }
            }
