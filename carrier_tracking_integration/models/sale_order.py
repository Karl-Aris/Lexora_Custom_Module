import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Field to display tracking number (from linked delivery)
    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)

    # Field to store latest tracking status
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        """Track FedEx shipment based on the linked delivery's carrier_tracking_ref."""
        for order in self:
            # Get the tracking number from the delivery (stock.picking)
            picking = order.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')
            if not picking:
                raise UserError(_("No outgoing delivery found for this Sale Order."))

            tracking_number = picking[0].carrier_tracking_ref
            if not tracking_number:
                raise UserError(_("No tracking number found on the delivery."))

            # Update the Sale Order tracking_number field
            order.tracking_number = tracking_number

            # Get the carrier and check if FedEx tracking is enabled
            carrier = picking[0].carrier_id
            if not carrier or carrier.tracking_carrier != 'fedex' or not carrier.tracking_integration_enabled:
                raise UserError(_("FedEx tracking is not configured for this delivery."))

            # Get FedEx token from carrier
            token = carrier._fedex_get_access_token()

            # Determine endpoint (sandbox/production)
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

            # Parse FedEx response
            data = response.json()
            results = data.get("output", {}).get("completeTrackResults", [])
            if results and results[0].get("trackResults"):
                status_detail = results[0]["trackResults"][0].get("latestStatusDetail", {})
                order.tracking_status = status_detail.get("statusByLocale", "Unknown")
            else:
                order.tracking_status = "No status available"

            # Show popup
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, order.tracking_status),
                    "type": "rainbow_man",
                }
            }
