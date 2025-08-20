from odoo import models, _
from odoo.exceptions import UserError
import requests

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_track_shipment(self):
        for order in self:
            if not order.x_delivery_out or not order.x_delivery_out.carrier_tracking_ref:
                raise UserError(_("No delivery tracking number found."))

            tracking_number = order.x_delivery_out.carrier_tracking_ref
            carrier = order.x_delivery_out.carrier_id

            if not carrier or carrier.tracking_carrier != 'fedex' or not carrier.tracking_integration_enabled:
                raise UserError(_("FedEx tracking is not configured for this delivery."))

            # Get token via carrier method
            token = carrier._fedex_get_access_token()

            # Determine FedEx API endpoint
            sandbox_mode = self.env['ir.config_parameter'].sudo().get_param('fedex_sandbox_mode', 'True') == 'True'
            url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers" if sandbox_mode else "https://apis.fedex.com/track/v1/trackingnumbers"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

            payload = {
                "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
                "includeDetailedScans": False
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx request error: %s") % str(e))

            # Parse response safely
            data = response.json()
            results = data.get("output", {}).get("completeTrackResults", [])
            if results and results[0].get("trackResults"):
                status_detail = results[0]["trackResults"][0].get("latestStatusDetail", {})
                order.tracking_status = status_detail.get("statusByLocale", "Unknown")
            else:
                order.tracking_status = "No status available"

            # Return popup notification
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, order.tracking_status),
                    "type": "rainbow_man",  # fun effect, you can change to "info" if preferred
                }
            }
