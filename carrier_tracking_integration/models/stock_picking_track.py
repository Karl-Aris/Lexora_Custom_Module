import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    tracking_status = fields.Text("Tracking Status (Last Response)", readonly=True)

    def action_track_shipment(self):
        for picking in self:
            if not picking.carrier_tracking_ref:
                raise UserError(_("Please set a Tracking Reference (carrier_tracking_ref) first."))

            carrier = picking.carrier_id
            if not carrier:
                raise UserError(_("Please select a Delivery Carrier on this transfer."))

            vendor = carrier.carrier_vendor or "none"

            try:
                if vendor == "ups":
                    picking._track_with_ups()
                elif vendor == "xpo":
                    picking._track_with_xpo()
                else:
                    raise UserError(_("This carrier is not configured for API tracking. "
                                      "Set 'Carrier Vendor' to UPS or XPO on the carrier."))
            except UserError:
                raise
            except Exception as e:
                raise UserError(_("Tracking error: %s") % str(e))

    # ---------------- UPS ----------------
    def _ups_endpoints(self, carrier):
        if carrier.ups_use_sandbox:
            base_auth = "https://wwwcie.ups.com/security/v1/oauth/token"
            base_track = "https://wwwcie.ups.com/api/track/v1/details/"
        else:
            base_auth = "https://onlinetools.ups.com/security/v1/oauth/token"
            base_track = "https://onlinetools.ups.com/api/track/v1/details/"
        return base_auth, base_track

    def _track_with_ups(self):
        self.ensure_one()
        c = self.carrier_id

        # Minimal credential checks (adjust to your UPS app setup)
        client_id = c.ups_access_key
        client_secret = c.ups_client_secret
        if not client_id or not client_secret:
            raise UserError(_("UPS credentials are missing on the carrier (Access Key/Client ID & Client Secret)."))

        token_url, base_track = self._ups_endpoints(c)

        # 1) OAuth token
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_data = {"grant_type": "client_credentials"}
        auth = (client_id, client_secret)
        token_res = requests.post(token_url, headers=token_headers, data=token_data, auth=auth, timeout=60)
        if token_res.status_code != 200:
            raise UserError(_("UPS OAuth error: %s") % token_res.text)
        token = token_res.json().get("access_token")
        if not token:
            raise UserError(_("UPS OAuth response missing access_token."))

        # 2) Tracking call
        track_url = f"{base_track}{self.carrier_tracking_ref}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        res = requests.get(track_url, headers=headers, timeout=60)
        self.tracking_status = res.text
        if res.status_code >= 400:
            self.message_post(body=_("UPS Tracking failed:<br/><pre>%s</pre>") % (res.text))
            raise UserError(_("UPS Tracking API returned error (HTTP %s).") % res.status_code)

        try:
            data = res.json()
        except Exception:
            data = {"raw": res.text}

        # Post a compact summary to chatter
        summary = self._format_ups_summary(data)
        self.message_post(body=_("UPS Tracking Update:<br/><pre>%s</pre>") % summary)

    def _format_ups_summary(self, data):
        """Create a readable summary from UPS JSON."""
        try:
            shipments = data.get("trackResponse", {}).get("shipment", [])
            events = []
            for s in shipments:
                for p in s.get("package", []):
                    for a in p.get("activity", []):
                        desc = a.get("status", {}).get("description")
                        dt = a.get("date") or ""
                        tm = a.get("time") or ""
                        loc = (a.get("location", {}) or {}).get("address", {})
                        city = loc.get("city") or ""
                        st = loc.get("stateProvince") or ""
                        co = loc.get("country") or ""
                        events.append(f"{dt} {tm} {city} {st} {co} - {desc}")
            if not events:
                return json.dumps(data, indent=2)[:4000]
            # Return last few events
            return "\n".join(events[:10])
        except Exception:
            return json.dumps(data, indent=2)[:4000]

    # ---------------- XPO (placeholder) ----------------
    def _track_with_xpo(self):
        self.ensure_one()
        c = self.carrier_id
        api_key = c.xpo_api_key
        if not api_key:
            raise UserError(_("XPO API Key is missing on the carrier."))

        # Adjust to your XPO contract; demo placeholder below:
        # NOTE: Replace with the actual XPO tracking endpoint your rep gives you.
        base_url = "https://api.sandbox.xpo.com" if c.xpo_use_sandbox else "https://api.xpo.com"
        url = f"{base_url}/track?pro={self.carrier_tracking_ref}"
        headers = {"apikey": api_key}
        res = requests.get(url, headers=headers, timeout=60)
        self.tracking_status = res.text

        if res.status_code >= 400:
            self.message_post(body=_("XPO Tracking failed:<br/><pre>%s</pre>") % (res.text))
            raise UserError(_("XPO Tracking API returned error (HTTP %s).") % res.status_code)

        try:
            data = res.json()
        except Exception:
            data = {"raw": res.text}

        # Post readable version (for now, raw JSON or key fields)
        summary = json.dumps(data, indent=2)[:4000]
        self.message_post(body=_("XPO Tracking Update:<br/><pre>%s</pre>") % summary)
