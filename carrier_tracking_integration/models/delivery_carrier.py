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
        self.ensure_one()
        url = "https://apis-sandbox.fedex.com/oauth/token" if self.tracking_sandbox_mode else "https://apis.fedex.com/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        resp = requests.post(url, data=data, headers=headers, timeout=15)
        if resp.status_code != 200:
            raise UserError(_("FedEx OAuth failed: %s") % resp.text)
        return resp.json().get("access_token")
