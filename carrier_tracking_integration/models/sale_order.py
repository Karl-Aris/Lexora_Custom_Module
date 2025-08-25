import logging
import requests
import uuid
import time
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def _get_fedex_token(self, carrier):
        """Fetch FedEx OAuth token for the given delivery carrier (with caching)."""
        if not carrier.fedex_client_id or not carrier.fedex_client_secret:
            raise UserError(_("FedEx credentials are missing on the delivery carrier."))

        if carrier.fedex_token_cache and carrier.fedex_token_expiry and time.time() < carrier.fedex_token_expiry:
            return carrier.fedex_token_cache

        base_url = "https://apis-sandbox.fedex.com" if carrier.fedex_use_sandbox else "https://apis.fedex.com"
        url = f"{base_url}/oauth/token"

        payload = {
            'grant_type': 'client_credentials',
            'client_id': carrier.fedex_client_id,
            'client_secret': carrier.fedex_client_secret
        }
        headers = {'Content-Type': "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)

            if not token:
                raise UserError(_("No access token returned by FedEx."))

            carrier.write({
                "fedex_token_cache": token,
                "fedex_token_expiry": time.time() + expires_in,
            })

            return token
        except requests.exceptions.RequestException as e:
            raise UserError(_("FedEx token request error: %s") % str(e))

    def action_track_shipment(self):
        """Track FedEx shipment using the configured Delivery Carrier REST API."""
        for order in self:
            if not order.carrier_id:
                raise UserError(_("No delivery carrier set for this order."))
            if not order.carrier_tracking_ref:
                raise UserError(_("No tracking number set for this order."))

            carrier = order.carrier_id
            if carrier.delivery_type != "fixed" and not (carrier.fedex_client_id and carrier.fedex_client_secret):
                raise UserError(_("Selected carrier is not configured for FedEx REST."))

            token = self._get_fedex_token(carrier)
            tracking_number = order.carrier_tracking_ref

            base_url = "https://apis-sandbox.fedex.com" if carrier.fedex_use_sandbox else "https://apis.fedex.com"
            track_url = f"{base_url}/track/v1/trackingnumbers"

            payload = {
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
                resp = requests.post(track_url, headers=headers, json=payload, timeout=25)
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

                order.write({
                    "tracking_status": status,
                    "tracking_number": tracking_number,
                })

                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                        "type": "rainbow_man",
                    }
                }
            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx tracking request error: %s") % str(e))
