# carrier_tracking_integration/models/sale_order.py
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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
            sandbox_mode = self.env['ir.config_parameter'].sudo().get_param('fedex_sandbox_mode', 'True') == 'True'
            url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers" if sandbox_mode else "https://apis.fedex.com/track/v1/trackingnumbers"

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
            results = data.get("output", {}).get("completeTrackResults", [])

            status = "Unknown"
            if results:
                track_results = results[0].get("trackResults", [])
                if track_results:
                    result = track_results[0]

                    # Handle invalid number case
                    if "error" in result:
                        error_info = result["error"]
                        status = error_info.get("message", "Tracking number not found")
                    else:
                        status_detail = result.get("latestStatusDetail", {})
                        scan_events = result.get("scanEvents", [])

                        # Priority: last scan event > description > statusByLocale
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
