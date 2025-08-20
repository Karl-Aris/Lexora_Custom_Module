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
            picking = order.picking_ids.filtered(lambda p: p.picking_type_code == "outgoing")
            if not picking:
                raise UserError(_("No outgoing delivery found for this Sale Order."))

            picking = picking[0]
            tracking_number = picking.carrier_tracking_ref
            if not tracking_number:
                raise UserError(_("No tracking number found on the delivery."))

            order.tracking_number = tracking_number

            carrier = picking.carrier_id
            if not carrier or not carrier.tracking_integration_enabled:
                raise UserError(_("Tracking integration is not configured for this delivery."))

            status = "Unknown"

            # --------------------------
            # FedEx Tracking
            # --------------------------
            if carrier.tracking_carrier == "fedex":
                token = carrier._fedex_get_access_token()
                url = (
                    "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
                    if carrier.tracking_sandbox_mode
                    else "https://apis.fedex.com/track/v1/trackingnumbers"
                )
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
                    _logger.info("FedEx Track Response (%s): %s", tracking_number, response.text)
                except requests.exceptions.RequestException as e:
                    raise UserError(_("FedEx request error: %s") % str(e))

                data = response.json()
                results = data.get("output", {}).get("completeTrackResults", [])

                if results:
                    track_results = results[0].get("trackResults", [])
                    if track_results:
                        result = track_results[0]

                        if "error" in result:
                            error_info = result["error"]
                            status = error_info.get("message", "Tracking number not found")
                        else:
                            status_detail = result.get("latestStatusDetail", {})
                            scan_events = result.get("scanEvents", [])

                            if scan_events:
                                status = scan_events[-1].get("eventDescription", status)
                            elif status_detail.get("description"):
                                status = status_detail["description"]
                            elif status_detail.get("statusByLocale"):
                                status = status_detail["statusByLocale"]

            # --------------------------
            # UPS Tracking
            # --------------------------
            elif carrier.tracking_carrier == "ups":
                try:
                    status = carrier._ups_track_shipment(tracking_number)
                except Exception as e:
                    raise UserError(_("UPS request error: %s") % str(e))

            else:
                raise UserError(_("Unsupported carrier: %s") % carrier.tracking_carrier)

            # Save status
            order.tracking_status = status

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                    "type": "rainbow_man",
                }
            }
