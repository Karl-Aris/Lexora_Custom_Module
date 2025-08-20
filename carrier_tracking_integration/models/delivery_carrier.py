# carrier_tracking_integration/models/delivery_carrier.py
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
    tracking_secret_key = fields.Char("Secret Key")
    tracking_sandbox_mode = fields.Boolean("Use Sandbox Mode", default=True)

    def _fedex_get_access_token(self):
        """Fetch OAuth access token from FedEx (sandbox or production)."""
        self.ensure_one()
        url = (
            "https://apis-sandbox.fedex.com/oauth/token"
            if self.tracking_sandbox_mode
            else "https://apis.fedex.com/oauth/token"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=15)
        except requests.exceptions.RequestException as e:
            raise UserError(_("FedEx OAuth request failed: %s") % str(e))

        if resp.status_code != 200:
            raise UserError(_("FedEx OAuth failed: %s") % resp.text)

        token = resp.json().get("access_token")
        if not token:
            raise UserError(_("FedEx OAuth response did not include an access token."))

        return token

    def action_test_tracking_connection(self):
        """Button to test FedEx API connection from carrier form."""
        self.ensure_one()
        if self.tracking_carrier != "fedex":
            raise UserError(_("This test is only available for FedEx carriers."))

        try:
            token = self._fedex_get_access_token()
            if not token:
                raise UserError(_("FedEx did not return an access token. Please check your API key and secret."))
        except Exception as e:
            raise UserError(_("FedEx connection failed: %s") % str(e))

        return {
            "effect": {
                "fadeout": "slow",
                "message": _("✅ FedEx connection successful. Token acquired."),
                "type": "rainbow_man",
            }
        }
