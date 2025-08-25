from odoo import models, fields, api
import requests
from requests.auth import HTTPBasicAuth
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fedex_tracking_number = fields.Char(string="FedEx Tracking Number")
    fedex_tracking_status = fields.Char(string="FedEx Tracking Status", readonly=True)

    def action_fedex_track(self):
        """Fetch FedEx tracking status using FedEx API."""
        self.ensure_one()
        if not self.fedex_tracking_number:
            raise ValueError("No FedEx tracking number set on this order.")

        # Example FedEx API endpoint and credentials (sandbox)
        url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
        client_id = self.env['ir.config_parameter'].sudo().get_param('fedex.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('fedex.client_secret')

        # Request access token
        try:
            token_resp = requests.post(
                "https://apis-sandbox.fedex.com/oauth/token",
                auth=HTTPBasicAuth(client_id, client_secret),
                data={'grant_type': 'client_credentials'},
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
        except Exception as e:
            _logger.error("FedEx token request failed: %s", e)
            raise ValueError("FedEx token request failed. Check your credentials.")

        # Request tracking info
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": self.fedex_tracking_number}}],
            "includeDetailedScans": True
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            status = data.get('output', {}).get('completeTrackResults', [{}])[0].get('trackResults', [{}])[0].get('latestStatusDetail', {}).get('description')
            self.fedex_tracking_status = status or 'Unknown'
        except Exception as e:
            _logger.error("FedEx tracking request failed: %s", e)
            raise ValueError("FedEx tracking request failed. Check tracking number or network.")

        return True
