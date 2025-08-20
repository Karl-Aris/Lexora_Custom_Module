from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_number = fields.Char("Tracking Number", compute="_compute_tracking_number", store=False)
    tracking_status = fields.Char("Tracking Status")

    def _compute_tracking_number(self):
        """Fetch tracking number from related delivery pickings"""
        for order in self:
            pickings = order.picking_ids.filtered(lambda p: p.carrier_tracking_ref)
            order.tracking_number = pickings[:1].carrier_tracking_ref if pickings else False

    def action_track_shipment(self):
        self.ensure_one()
        if not self.tracking_number:
            raise UserError(_("No tracking number found for this order."))

        carrier = self.carrier_id
        if not (carrier.tracking_integration_enabled and carrier.tracking_carrier == "fedex"):
            raise UserError(_("Tracking integration not configured for FedEx."))

        # Step 1: Get FedEx OAuth token
        token_url = "https://apis-sandbox.fedex.com/oauth/token"
        payload = {"grant_type": "client_credentials"}
        auth = (carrier.tracking_api_key, carrier.tracking_secret_key)
        token_response = requests.post(token_url, data=payload, auth=auth)
        if token_response.status_code != 200:
            raise UserError(_("Failed to authenticate with FedEx: %s") % token_response.text)
        access_token = token_response.json().get("access_token")

        # Step 2: Call FedEx Tracking API
        tracking_url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {"trackingInfo": [{"trackingNumberInfo": {"trackingNumber": self.tracking_number}}]}
        response = requests.post(tracking_url, headers=headers, json=body)

        if response.status_code != 200:
            raise UserError(_("Failed to fetch tracking status: %s") % response.text)

        data = response.json()
        status = (
            data.get("output", {})
                .get("completeTrackResults", [{}])[0]
                .get("trackResults", [{}])[0]
                .get("latestStatusDetail", {})
                .get("description")
        )

        self.tracking_status = status or "Unknown"

        return {
            "effect": {
                "fadeout": "slow",
                "message": _("Latest Status: %s") % self.tracking_status,
                "type": "rainbow_man",
            }
        }
