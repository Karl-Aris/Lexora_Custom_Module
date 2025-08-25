import logging
import requests
import uuid
import time
import json
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    _fedex_token_cache = None
    _token_expiry_time_cache = None

    def _get_fedex_token(self):
        """Fetch FedEx OAuth token (with caching)."""
        if self._fedex_token_cache and time.time() < self._token_expiry_time_cache:
            return self._fedex_token_cache

        client_id = self.env['ir.config_parameter'].sudo().get_param('fedex.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('fedex.client_secret')
        use_sandbox = self.env['ir.config_parameter'].sudo().get_param('fedex.use_sandbox', 'False') == 'True'

        if not client_id or not client_secret:
            raise UserError(_("FedEx credentials are not configured. Please set system parameters."))

        base_url = "https://apis-sandbox.fedex.com" if use_sandbox else "https://apis.fedex.com"
        url = f"{base_url}/oauth/token"

        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        headers = {'Content-Type': "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            new_token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)

            if new_token:
                SaleOrder._fedex_token_cache = new_token
                SaleOrder._token_expiry_time_cache = time.time() + expires_in
                return new_token
            else:
                raise UserError(_("No access token found from FedEx."))
        except requests.exceptions.RequestException as e:
            raise UserError(_("Error fetching FedEx token: %s") % str(e))

    def action_track_shipment(self):
        """Track FedEx shipment using REST API"""
        for order in self:
            if not order.carrier_id:
                raise UserError(_("No delivery carrier set for this order."))
            if not order.carrier_tracking_ref:
                raise UserError(_("No tracking number set for this order."))

            tracking_number = order.carrier_tracking_ref
            token = self._get_fedex_token()

            use_sandbox = self.env['ir.config_parameter'].sudo().get_param('fedex.use_sandbox', 'False') == 'True'
            base_url = "https://apis-sandbox.fedex.com" if use_sandbox else "https://apis.fedex.com"
            track_url = f"{base_url}/track/v1/trackingnumbers"

            track_payload = {
                "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
                "includeDetailedScans": True
            }
            headers = {
                'Content-Type': "application/json",
                'X-locale': "en_US",
                'Authorization': f"Bearer {token}",
                'x-customer-transaction-id': str(uuid.uuid4())
            }

            try:
                resp = requests.post(track_url, headers=headers, json=track_payload, timeout=25)
                resp.raise_for_status()
                data = resp.json()
                results = data.get("output", {}).get("completeTrackResults", [])
                status = "Unknown"

                if results:
                    track_results = results[0].get("trackResults", [])
                    if track_results:
                        result = track_results[0]
                        if "error" in result:
                            status = result["error"].get("message", "Tracking number not found")
                        else:
                            status_detail = result.get("latestStatusDetail", {})
                            status = status_detail.get("statusByLocale", "Unknown")

                order.tracking_status = status
                order.tracking_number = tracking_number

                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                        "type": "rainbow_man",
                    }
                }

            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx tracking request error: %s") % str(e))
