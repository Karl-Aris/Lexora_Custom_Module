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

    fedex_tracking_number = fields.Char(string="FedEx Tracking Number", copy=False)
    fedex_tracking_status = fields.Char(string="FedEx Tracking Status", readonly=True, copy=False)

    # Token cache (class-level)
    _fedex_token_cache = None
    _fedex_token_expiry_cache = None

    # ------------------------------
    # FedEx OAuth Token
    # ------------------------------
    def _get_fedex_token(self):
        """Fetch FedEx OAuth token (with caching)."""
        if (
            self._fedex_token_cache
            and time.time() < self._fedex_token_expiry_cache
        ):
            _logger.info("Using cached FedEx token.")
            return self._fedex_token_cache

        url = "https://apis-sandbox.fedex.com/oauth/token"  # Sandbox URL
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.env["ir.config_parameter"].sudo().get_param("fedex.client_id"),
            "client_secret": self.env["ir.config_parameter"].sudo().get_param("fedex.client_secret"),
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            resp = requests.post(url, data=payload, headers=headers, timeout=20)
            _logger.info("FedEx OAuth Response: %s", resp.text)

            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                if not token:
                    raise UserError(_("No access token returned from FedEx."))

                # Cache
                SaleOrder._fedex_token_cache = token
                SaleOrder._fedex_token_expiry_cache = time.time() + expires_in
                return token
            else:
                raise UserError(_("FedEx token request error: %s") % resp.text)

        except requests.exceptions.RequestException as e:
            _logger.error("FedEx token error: %s", str(e))
            raise UserError(_("FedEx token request error: %s") % str(e))

    # ------------------------------
    # Tracking Action
    # ------------------------------
    def action_fedex_track(self):
        """Track shipment via FedEx REST API."""
        for order in self:
            if not order.fedex_tracking_number:
                raise UserError(_("No FedEx tracking number set on this order."))

            token = self._get_fedex_token()
            track_url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"

            payload = {
                "trackingInfo": [
                    {"trackingNumberInfo": {"trackingNumber": order.fedex_tracking_number}}
                ],
                "includeDetailedScans": True,
            }

            headers = {
                "Content-Type": "application/json",
                "X-locale": "en_US",
                "Authorization": "Bearer " + token,
                "x-customer-transaction-id": str(uuid.uuid4()),
            }

            try:
                resp = requests.post(track_url, headers=headers, json=payload, timeout=25)
                resp.raise_for_status()
                _logger.info("FedEx Track Response: %s", resp.text)

                data = resp.json()
                results = data.get("output", {}).get("completeTrackResults", [])
                status = "Unknown"

                if results:
                    track_results = results[0].get("trackResults", [])
                    if track_results:
                        res = track_results[0]
                        if "error" in res:
                            status = res["error"].get("message", "Tracking not found")
                        else:
                            status_detail = res.get("latestStatusDetail", {})
                            status = status_detail.get("statusByLocale", "Unknown")

                order.fedex_tracking_status = status

                order.message_post(
                    body=_("FedEx Tracking updated: %s → %s")
                    % (order.fedex_tracking_number, status)
                )

                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": _("Tracking Status: %s") % status,
                        "type": "rainbow_man",
                    }
                }

            except requests.exceptions.RequestException as e:
                _logger.error("FedEx tracking error: %s", str(e))
                raise UserError(_("FedEx tracking request error: %s") % str(e))
