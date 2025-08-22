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
    
    response = requests.post(url, data=payload, headers=headers)
    
    print(response.text)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        response_data = response.json()
        
        # Extract the access token
        new_token = response_data.get('access_token')
        
        if new_token:
            print("Access Token:", new_token)
        else:
            print("No access token found in the response.")
    else:
        print("Error:", response.status_code, response.text)

    tracking_number = fields.Char(string="Tracking Number", readonly=True, copy=False)
    tracking_status = fields.Char(string="Tracking Status", readonly=True, copy=False)

    def action_track_shipment(self):
        """Track shipment from sale order using carrier logic"""
        for order in self:
            if not order.carrier_id:
                raise UserError(_("No delivery carrier set for this order."))
            if not order.tracking_number:
                raise UserError(_("No tracking number available for this order."))

            carrier = order.carrier_id
            tracking_number = order.tracking_number
            status = "Unknown"

            # ───────────────────────────── FedEx (real API)
            if carrier.tracking_carrier == "fedex":
                # token = carrier._fedex_get_access_token()
                # url = (
                #     "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
                #     if carrier.tracking_sandbox_mode
                #     else "https://apis.fedex.com/track/v1/trackingnumbers"
                # )
                # headers = {
                #     "Content-Type": "application/json",
                #     "Authorization": f"Bearer {token}",
                # }
                # payload = {
                #     "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
                #     "includeDetailedScans": True,
                # }
                url = "https://apis-sandbox.fedex.com/track/v1/tcn"

                payload = {
                  "trackingInfo": [
                    {
                      "trackingNumberInfo": {
                        "trackingNumber": tracking_number
                      }
                    }
                  ],
                  "includeDetailedScans": true
                }
                headers = {
                    'Content-Type': "application/json",
                    'X-locale': "en_US",
                    'Authorization': "Bearer " + new_token,
                    }
                
                response = requests.post(url, data=payload, headers=headers)
                
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=25)
                    resp.raise_for_status()
                    _logger.info("FedEx Track Response (%s): %s", tracking_number, resp.text)
                    data = resp.json()
                except requests.exceptions.RequestException as e:
                    raise UserError(_("FedEx request error: %s") % str(e))

                results = data.get("output", {}).get("completeTrackResults", [])
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

            # ───────────────────────────── UPS (placeholder)
            elif carrier.tracking_carrier == "ups":
                status = carrier._ups_track_shipment(tracking_number)

            # ───────────────────────────── Other carriers (placeholders)
            elif carrier.tracking_carrier == "xpo":
                status = carrier._xpo_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "estes":
                status = carrier._estes_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "roadrunner":
                status = carrier._roadrunner_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "central_transport":
                status = carrier._central_transport_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "jbhunt":
                status = carrier._jbhunt_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "titanium":
                status = carrier._titanium_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "pitt_ohio":
                status = carrier._pitt_ohio_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "ceva":
                status = carrier._ceva_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "tforce":
                status = carrier._tforce_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "tst_overland":
                status = carrier._tst_overland_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "efw":
                status = carrier._efw_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "abf":
                status = carrier._abf_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "wgd":
                status = carrier._wgd_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "aduie_pyle":
                status = carrier._aduie_pyle_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "saia":
                status = carrier._saia_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "ch_robinson":
                status = carrier._ch_robinson_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "ait":
                status = carrier._ait_track_shipment(tracking_number)
            elif carrier.tracking_carrier == "frontline":
                status = carrier._frontline_track_shipment(tracking_number)
            else:
                raise UserError(_("Unsupported carrier: %s") % carrier.tracking_carrier)

            # Save status in order field
            order.tracking_status = status

            # Show rainbow man popup
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Tracking Status for %s: %s") % (tracking_number, status),
                    "type": "rainbow_man",
                }
            }
