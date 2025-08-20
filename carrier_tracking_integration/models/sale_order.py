# carrier_tracking_integration/models/sale_order.py
import requests
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        for order in self:
            picking = order.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')
            if not picking:
                raise UserError(_("No outgoing delivery found for this Sale Order."))

            picking = picking[0]
            tracking_number = picking.carrier_tracking_ref
            if not tracking_number:
                raise UserError(_("No tracking number found on the delivery."))

            order.tracking_number = tracking_number

            carrier = picking.carrier_id
            if not carrier or carrier.tracking_carrier != 'fedex' or not carrier.tracking_integration_enabled:
                raise UserError(_("FedEx tracking is not configured for this delivery."))

            token = carrier._fedex_get_access_token()

            # Use carrier-specific sandbox toggle
            if carrier.tracking_sandbox_mode:
                url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
            else:
                url = "https://apis.fedex.com/track/v1/trackingnumbers"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

            payload = {
                "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
                "includeDetailedScans": True,
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx request error: %s") % str(e))

            data = response.json()
            _logger.info("FedEx API Response for tracking %s: %s", tracking_number, data)

            results = data.get("output", {}).get("completeTrackResults", [])

            status = "Unknown"
            if results:
                track_results = results[0].get("trackResults", [])
                if track_results:
                    result = track_results[0]

                    # Case 1: Explicit FedEx error
                    if "error" in result:
                        status = result["error"].get("message", "Invalid tracking number")

                    # Case 2: Tracking number is not assigned (invalid / fake)
                    elif not result.get("trackingNumberInfo", {}).get("assigned", True):
                        status = "Invalid tracking number"

                    # Case 3: Valid tracking number, extract latest status
                    else:
                        status_detail = result.get("latestStatusDetail", {})
                        scan_events = result.get("scanEvents", [])

                        if scan_events:
                            status = scan_events[-1].get("eventDescription", status)
                        elif status_detail.get("description"):
                            status = status_detail["description"]
                        elif status_detail.get("statusByLocale"):
                            status = status_detail["statusByLocale"]

            order.tracking_status = status

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                    "type": "rainbow_man",
                }
            }
