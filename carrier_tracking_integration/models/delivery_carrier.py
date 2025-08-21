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
        ("estes", "Estes Express Lines"),
        ("roadrunner", "Roadrunner Transportation Services"),
        ("central_transport", "Central Transport"),
        ("jbhunt", "JB Hunt Dedicated"),
        ("titanium", "Titanium Logistics"),
        ("pitt_ohio", "Pitt Ohio Express"),
        ("ceva", "CEVA Logistics"),
        ("tforce", "TForce Freight Inc"),
        ("tst_overland", "TST Overland"),
        ("efw", "EFW"),
        ("abf", "ABF Freight System"),
        ("wgd", "WGD Midwest (AM Home)"),
        ("aduie_pyle", "A Duie Pyle Inc"),
        ("saia", "Saia Motor Freight Line"),
        ("ch_robinson", "C.H. Robinson"),
        ("ait", "AIT Worldwide"),
        ("frontline", "Frontline Carrier Systems USA Inc"),
    ], string="Carrier")
    tracking_api_key = fields.Char("API Key")
    tracking_account_number = fields.Char("Account Number")
    tracking_secret_key = fields.Char("Secret Key")
    tracking_sandbox_mode = fields.Boolean("Use Sandbox Mode", default=True)

    # ---------------- FedEx ----------------
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

    # ---------------- Carrier Stubs ----------------
    def _xpo_track_shipment(self, tracking_number): _logger.info("XPO %s", tracking_number); return "XPO tracking not yet implemented"
    def _estes_track_shipment(self, tracking_number): _logger.info("Estes %s", tracking_number); return "Estes tracking not yet implemented"
    def _roadrunner_track_shipment(self, tracking_number): _logger.info("Roadrunner %s", tracking_number); return "Roadrunner tracking not yet implemented"
    def _central_transport_track_shipment(self, tracking_number): _logger.info("Central %s", tracking_number); return "Central Transport tracking not yet implemented"
    def _jbhunt_track_shipment(self, tracking_number): _logger.info("JB Hunt %s", tracking_number); return "JB Hunt tracking not yet implemented"
    def _titanium_track_shipment(self, tracking_number): _logger.info("Titanium %s", tracking_number); return "Titanium tracking not yet implemented"
    def _pitt_ohio_track_shipment(self, tracking_number): _logger.info("Pitt Ohio %s", tracking_number); return "Pitt Ohio tracking not yet implemented"
    def _ceva_track_shipment(self, tracking_number): _logger.info("CEVA %s", tracking_number); return "CEVA tracking not yet implemented"
    def _tforce_track_shipment(self, tracking_number): _logger.info("TForce %s", tracking_number); return "TForce tracking not yet implemented"
    def _tst_overland_track_shipment(self, tracking_number): _logger.info("TST Overland %s", tracking_number); return "TST Overland tracking not yet implemented"
    def _efw_track_shipment(self, tracking_number): _logger.info("EFW %s", tracking_number); return "EFW tracking not yet implemented"
    def _abf_track_shipment(self, tracking_number): _logger.info("ABF %s", tracking_number); return "ABF tracking not yet implemented"
    def _wgd_track_shipment(self, tracking_number): _logger.info("WGD %s", tracking_number); return "WGD Midwest tracking not yet implemented"
    def _aduie_pyle_track_shipment(self, tracking_number): _logger.info("A Duie Pyle %s", tracking_number); return "A Duie Pyle tracking not yet implemented"
    def _saia_track_shipment(self, tracking_number): _logger.info("Saia %s", tracking_number); return "Saia tracking not yet implemented"
    def _ch_robinson_track_shipment(self, tracking_number): _logger.info("CH Robinson %s", tracking_number); return "C.H. Robinson tracking not yet implemented"
    def _ait_track_shipment(self, tracking_number): _logger.info("AIT %s", tracking_number); return "AIT tracking not yet implemented"
    def _frontline_track_shipment(self, tracking_number): _logger.info("Frontline %s", tracking_number); return "Frontline tracking not yet implemented"

    # ---------------- Test Connection ----------------
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
            raise UserError(_("UPS test connection placeholder ✅"))

        elif self.tracking_carrier in [
            "xpo", "estes", "roadrunner", "central_transport", "jbhunt",
            "titanium", "pitt_ohio", "ceva", "tforce", "tst_overland", "efw",
            "abf", "wgd", "aduie_pyle", "saia", "ch_robinson", "ait", "frontline"
        ]:
            raise UserError(_("%s test connection placeholder ✅") % self.tracking_carrier.upper())

        else:
            raise UserError(_("Carrier not supported yet: %s") % self.tracking_carrier)
