import requests
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    carrier_type = fields.Selection([
        ("xpo", "XPO Logistics"),
        ("ups", "UPS"),
    ], string="Carrier")
    tracking_number = fields.Char("Tracking Number")
    tracking_status = fields.Text("Tracking Status")

    def track_shipment(self):
        for rec in self:
            if not rec.tracking_number or not rec.carrier_type:
                raise ValueError("Tracking number or carrier is missing.")

            if rec.carrier_type == "xpo":
                rec._track_xpo()
            elif rec.carrier_type == "ups":
                rec._track_ups()

    def _track_xpo(self):
        config = self.env["ir.config_parameter"].sudo()
        api_key = config.get_param("carrier_tracking_integration.xpo_api_key")

        if not api_key:
            raise ValueError("XPO API key not configured.")

        url = f"https://api.xpo.com/track?pro={self.tracking_number}"
        headers = {"apikey": api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.tracking_status = str(data)
            self.message_post(body=f"XPO Tracking Update: {data}")
        else:
            raise ValueError(f"XPO API Error: {response.text}")

    def _track_ups(self):
        config = self.env["ir.config_parameter"].sudo()
        client_id = config.get_param("carrier_tracking_integration.ups_client_id")
        client_secret = config.get_param("carrier_tracking_integration.ups_client_secret")

        if not client_id or not client_secret:
            raise ValueError("UPS API credentials not configured.")

        # Step 1: Get Access Token
        token_url = "https://wwwcie.ups.com/security/v1/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}
        auth = (client_id, client_secret)
        token_res = requests.post(token_url, headers=headers, data=data, auth=auth)

        if token_res.status_code != 200:
            raise ValueError(f"UPS Auth Error: {token_res.text}")

        token = token_res.json().get("access_token")

        # Step 2: Call UPS Tracking API
        track_url = f"https://wwwcie.ups.com/api/track/v1/details/{self.tracking_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        track_res = requests.get(track_url, headers=headers)

        if track_res.status_code == 200:
            data = track_res.json()
            self.tracking_status = str(data)
            self.message_post(body=f"UPS Tracking Update: {data}")
        else:
            raise ValueError(f"UPS API Error: {track_res.text}")
