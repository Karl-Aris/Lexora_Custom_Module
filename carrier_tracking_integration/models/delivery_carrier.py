# carrier_tracking_integration/models/delivery_carrier.py
import requests
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_integration_enabled = fields.Boolean("Enable Tracking Integration")
    tracking_carrier = fields.Selection([
        ("ups", "UPS"),
        ("fedex", "FedEx"),
        ("dhl", "DHL"),
    ], string="Carrier")
    tracking_api_key = fields.Char("API Key / Client ID")
    tracking_account_number = fields.Char("Account Number")
    tracking_secret_key = fields.Char("Secret Key / Client Secret")
    tracking_sandbox_mode = fields.Boolean("Use Sandbox Mode", default=True)

    # --------------------------
    # FedEx
    # --------------------------
    def _fedex_get_access_token(self):
        self.ensure_one()
        url = "https://apis-sandbox.fedex.com/oauth/token" if self.tracking_sandbox_mode else "https://apis.fedex.com/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        resp = requests.post(url, data=data, headers=headers, timeout=15)
        _logger.info("FedEx Auth Response: %s", resp.text)
        if resp.status_code != 200:
            raise UserError(_("FedEx OAuth failed: %s") % resp.text)
        return resp.json().get("access_token")

    # --------------------------
    # UPS
    # --------------------------
    def _ups_get_access_token(self):
        """UPS OAuth 2.0 authentication"""
        self.ensure_one()
        url = "https://wwwcie.ups.com/security/v1/oauth/token" if self.tracking_sandbox_mode else "https://onlinetools.ups.com/security/v1/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        resp = requests.post(url, data=data, headers=headers, timeout=15)
        _logger.info("UPS Auth Response: %s", resp.text)
        if resp.status_code != 200:
            raise UserError(_("UPS OAuth failed: %s") % resp.text)
        return resp.json().get("access_token")

    def _ups_track_shipment(self, tracking_number):
        """UPS shipment tracking"""
        self.ensure_one()
        token = self._ups_get_access_token()

        url = (
            f"https://wwwcie.ups.com/api/track/v1/details/{tracking_number}"
            if self.tracking_sandbox_mode
            else f"https://onlinetools.ups.com/api/track/v1/details/{tracking_number}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        resp = requests.get(url, headers=headers, timeout=20)
        _logger.info("UPS Track Response (%s): %s", tracking_number, resp.text)

        if resp.status_code != 200:
            raise UserError(_("UPS tracking failed: %s") % resp.text)

        data = resp.json()
        status = "Unknown"

        track_response = data.get("trackResponse", {})
        shipment = track_response.get("shipment", [])
        if shipment:
            package = shipment[0].get("package", [])
            if package:
                activity = package[0].get("activity", [])
                if activity:
                    status = activity[0].get("status", {}).get("description", status)

        return status
