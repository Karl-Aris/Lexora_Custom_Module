import logging
import requests
import uuid
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        """Track shipment via FedEx REST API"""
        for order in self:
            if not order.carrier_id or order.carrier_id.delivery_type != "fedex_rest":
                raise UserError(_("This order is not using FedEx REST as carrier."))
            if not order.carrier_tracking_ref:
                raise UserError(_("No tracking number set for this order."))

            carrier = order.carrier_id
            token = carrier._get_fedex_token()

            track_url = f"{carrier._get_fedex_base_url()}/track/v1/trackingnumbers"
            payload = {
                "trackingInfo": [
                    {"trackingNumberInfo": {"trackingNumber": order.carrier_tracking_ref}}
                ],
                "includeDetailedScans": True,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "X-locale": "en_US",
                "x-customer-transaction-id": str(uuid.uuid4()),
            }

            try:
                resp = requests.post(track_url, json=payload, headers=headers, timeout=25)
                _logger.info("FedEx Track Response: %s", resp.text)
                resp.raise_for_status()
                data = resp.json()

                results = data.get("output", {}).get("completeTrackResults", [])
                status = "Unknown"
                if results:
                    track_results = results[0].get("trackResults", [])
                    if track_results:
                        latest = track_results[0]
                        detail = latest.get("latestStatusDetail", {})
                        status = detail.get("statusByLocale", "Unknown")

                order.tracking_number = order.carrier_tracking_ref
                order.tracking_status = status

                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": _("Tracking Status for %s: %s") % (order.carrier_tracking_ref, status),
                        "type": "rainbow_man",
                    }
                }

            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx tracking request error: %s") % str(e))
