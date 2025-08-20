import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_out_tracking_ref = fields.Char(
        string="Delivery Tracking Ref",
        related="x_delivery_out.carrier_tracking_ref",
        readonly=True,
        store=False
    )

    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        for order in self:
            if not order.delivery_out_tracking_ref:
                raise UserError(_("No delivery tracking number found."))

            tracking_number = order.delivery_out_tracking_ref

            # Get FedEx token from system parameters
            token = self.env["ir.config_parameter"].sudo().get_param("fedex_api_token")
            if not token:
                raise UserError(_("FedEx API token is missing. Please configure it in System Parameters."))

            url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"  # Sandbox endpoint
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            payload = {
                "trackingInfo": [
                    {"trackingNumberInfo": {"trackingNumber": tracking_number}}
                ]
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)
            except Exception as e:
                raise UserError(_("Request error: %s") % str(e))

            if response.status_code == 200:
                data = response.json()
                try:
                    status = (
                        data.get("output", {})
                        .get("completeTrackResults", [])[0]
                        .get("trackResults", [])[0]
                        .get("latestStatusDetail", {})
                        .get("statusByLocale", "Unknown")
                    )
                    order.tracking_status = status
                except Exception:
                    raise UserError(_("Unexpected FedEx response format: %s") % data)
            else:
                raise UserError(_("FedEx API error: %s") % response.text)
