import requests
from odoo import models, fields, _
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
    tracking_secret_key = fields.Char("Secret Key")  # FedEx also needs this

    def _fedex_get_access_token(self):
        """Get OAuth token from FedEx"""
        self.ensure_one()
        url = "https://apis-sandbox.fedex.com/oauth/token"  # Sandbox URL
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            raise UserError(_("FedEx OAuth failed: %s") % resp.text)
        return resp.json().get("access_token")

    def action_test_tracking_connection(self):
        for carrier in self:
            if not carrier.tracking_integration_enabled:
                raise UserError(_("Tracking integration is not enabled."))
            if not carrier.tracking_carrier:
                raise UserError(_("Please select a carrier."))
            if not carrier.tracking_api_key:
                raise UserError(_("Please provide API Key."))

            if carrier.tracking_carrier == "fedex":
                # Step 1: Get token
                token = carrier._fedex_get_access_token()

                # Step 2: Call tracking API with a test tracking number
                url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                body = {
                    "trackingInfo": [
                        {
                            "trackingNumberInfo": {
                                "trackingNumber": "123456789012"  # FedEx test number
                            }
                        }
                    ],
                    "includeDetailedScans": False
                }

                resp = requests.post(url, headers=headers, json=body)
                if resp.status_code == 200:
                    msg = _("FedEx test connection successful!")
                else:
                    raise UserError(_("FedEx API error: %s") % resp.text)

            elif carrier.tracking_carrier == "ups":
                msg = _("UPS test connection successful (stub).")
            elif carrier.tracking_carrier == "dhl":
                msg = _("DHL test connection successful (stub).")
            else:
                msg = _("Unknown carrier.")

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": msg,
                    "type": "rainbow_man",
                }
            }
