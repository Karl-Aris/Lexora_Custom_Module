# -*- coding: utf-8 -*-
import logging
import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    url = "https://apis-sandbox.fedex.com/oauth/token"

    payload = {
        'grant_type':'client_credentials',
        'client_id':'l770fae96d7b5144c9aec2ada941608b60',
        'client_secret':'8c2f94b246314d459bf711854201f0d4'
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded"
    }
    
    # Send request to get access token
    response = requests.post(url, data=payload, headers=headers)
    
    _logger.info("FedEx OAuth Response: %s", response.text)  # Logging the response for debugging

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        response_data = response.json()
        
        # Extract the access token
        new_token = response_data.get('access_token')
        
        if new_token:
            _logger.info("Access Token: %s", new_token)  # Log the access token
        else:
            _logger.error("No access token found in the response.")
    else:
        _logger.error("Error: %s %s", response.status_code, response.text)

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        """Track shipment from sale order using carrier logic"""
        for order in self:
            if not order.carrier_id:
                raise UserError(_("No delivery carrier set for this order."))
            # if not order.tracking_number:
            #     raise UserError(_("No tracking number available for this order."))

            carrier = order.carrier_id
            # tracking_number = order.tracking_number
            tracking_number = '9632080400676090940600881054121257'
            status = "Unknown"
            json_data = None

            # ───────────────────────────── FedEx (real API)
            if carrier.tracking_carrier == "fedex":
                track_url = "https://apis-sandbox.fedex.com/track/v1/tcn"

                track_payload = {
                  "trackingInfo": [
                    {
                      "trackingNumberInfo": {
                        "trackingNumber": tracking_number
                      }
                    }
                  ],
                  "includeDetailedScans": True  # Fixed typo: true -> True
                }
                track_headers = {
                    'Content-Type': "application/json",
                    'X-locale': "en_US",
                    'Authorization': "Bearer " + new_token,
                }

                
                try:
                    # Send POST request for tracking
                    resp = requests.post(track_url, headers=track_headers, json=track_payload, timeout=25)
                    resp.raise_for_status()
                    _logger.info("FedEx Track Response (%s): %s", tracking_number, resp.text)  # Log the response

                    data = resp.json()
                    results = data.get("output", {}).get("completeTrackResults", [])
                    json_data = results
                    _logger.info("JSON Data returned: %s", json.dumps(json_data, indent=4))  # Pretty-print JSON data
                    if results:
                        track_results = results[0].get("trackResults", [])
                        if track_results:
                            result = track_results[0]
                            if "error" in result:
                                status = result["error"].get("message", "Tracking number not found")
                            else:
                                status_detail = result.get("latestStatusDetail", {})
                                scan_events = result.get("scanEvents", [])
                                if scan_events:
                                    status = scan_events[-1].get("eventDescription", status)
                                elif status_detail.get("description"):
                                    status = status_detail["description"]
                                elif status_detail.get("statusByLocale"):
                                    status = status_detail["statusByLocale"]
                except requests.exceptions.RequestException as e:
                    _logger.error("FedEx request error: %s", str(e))  # Log the error
                    raise UserError(_("FedEx request error: %s") % str(e))

            # ───────────────────────────── Other carriers (placeholders)
            # You can add more carriers and their tracking logic here...

            # Save status in order field
            order.tracking_status = status
            order.tracking_number = tracking_number

            # Show rainbow man popup
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                    "type": "rainbow_man",
                }
            }
