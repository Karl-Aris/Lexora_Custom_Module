# carrier_tracking_integration/models/delivery_carrier.py
import requests
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_integration_enabled = fields.Boolean("Enable Tracking Integration")
    tracking_carrier = fields.Selection([
        ("ups", "UPS"),
        ("fedex", "FedEx"),
        ("xpo", "XPO Logistics"),
    ], string="Carrier")
    tracking_api_key = fields.Char("API Key")
    tracking_account_number = fields.Char("Account Number")
    tracking_secret_key = fields.Char("Secret Key")
    tracking_sandbox_mode = fields.Boolean("Use Sandbox Mode", default=True)

    def _fedex_get_access_token(self):
        self.ensure_one()
        url = (
            "https://apis-sandbox.fedex.com/oauth/token"
            if self.tracking_sandbox_mode
            else "https://apis.fedex.com/oauth/token"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.tracking_api_key,
            "client_secret": self.tracking_secret_key,
        }
        resp = requests.post(url, data=data, headers=headers, timeout=15)
        if resp.status_code != 200:
            try:
                err = resp.json()
                msg = err.get("error_description") or err.get("error") or resp.text
            except Exception:
                msg = resp.text
            raise UserError(_("FedEx OAuth failed: %s") % msg)
        return resp.json().get("access_token")

    def _xpo_track_shipment(self, tracking_number):
        self.ensure_one()
        # 🔧 TODO: Replace with real XPO API call once credentials/docs are available
        _logger.info("XPO Tracking called for %s", tracking_number)
        return "XPO tracking not yet implemented"

    def action_test_tracking_connection(self):
        self.ensure_one()
        if self.tracking_carrier == "fedex":
            try:
                token = self._fedex_get_access_token()
                if token:
                    raise UserError(_("FedEx connection successful ✅"))
            except Exception as e:
                raise UserError(_("FedEx connection failed: %s") % str(e))

        elif self.tracking_carrier == "ups":
            try:
                # Stub UPS test
                raise UserError(_("UPS test connection placeholder ✅"))
            except Exception as e:
                raise UserError(_("UPS connection failed: %s") % str(e))

        elif self.tracking_carrier == "xpo":
            try:
                # Stub XPO test
                raise UserError(_("XPO Logistics test connection placeholder ✅"))
            except Exception as e:
                raise UserError(_("XPO connection failed: %s") % str(e))

        else:
            raise UserError(_("Carrier not supported yet: %s") % self.tracking_carrier)
