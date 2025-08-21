import logging
import requests

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    # Master toggle + shared credentials
    tracking_integration_enabled = fields.Boolean("Enable Tracking Integration")

    # One dropdown for all carriers
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
        ("saia", "Saia Motor Freight Line, LLC"),
        ("ch_robinson", "C.H. Robinson"),
        ("ait", "AIT Worldwide"),
        ("frontline", "Frontline Carrier Systems USA Inc"),
    ], string="Carrier")

    # Generic credential fields usable per carrier (you can extend later per‑carrier)
    tracking_api_key = fields.Char("API Key")
    tracking_secret_key = fields.Char("Secret Key")
    tracking_account_number = fields.Char("Account Number")
    tracking_sandbox_mode = fields.Boolean("Use Sandbox Mode", default=True)

    # ───────────────────────────────────────────────────────── FedEx (real OAuth)
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
        resp = requests.post(url, data=data, headers=headers, timeout=20)
        if resp.status_code != 200:
            try:
                err = resp.json()
                msg = err.get("error_description") or err.get("error") or resp.text
            except Exception:
                msg = resp.text
            raise UserError(_("FedEx OAuth failed: %s") % msg)
        return resp.json().get("access_token")

    # ────────────────────────────────────────────────────── Placeholders (sandbox)
    # Each method returns a friendly placeholder until real API is wired.

    def _ups_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Implement UPS tracking (OAuth / API key as per UPS API spec)
        _logger.info("UPS sandbox tracking called for %s", tracking_number)
        return "UPS sandbox tracking not yet implemented"

    def _xpo_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: XPO Logistics tracking API
        _logger.info("XPO sandbox tracking called for %s", tracking_number)
        return "XPO sandbox tracking not yet implemented"

    def _estes_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Estes API → https://developer.estes-express.com/
        _logger.info("Estes sandbox tracking called for %s", tracking_number)
        return "Estes sandbox tracking not yet implemented"

    def _roadrunner_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Roadrunner via AfterShip → https://www.aftership.com/carriers/roadrunner-freight/api
        _logger.info("Roadrunner sandbox tracking called for %s", tracking_number)
        return "Roadrunner sandbox tracking not yet implemented"

    def _central_transport_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Central Transport via ShipEngine → https://www.shipengine.com/integrations/central-transport/
        _logger.info("Central Transport sandbox tracking called for %s", tracking_number)
        return "Central Transport sandbox tracking not yet implemented"

    def _jbhunt_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: JB Hunt Dedicated (API onboarding required)
        _logger.info("JB Hunt sandbox tracking called for %s", tracking_number)
        return "JB Hunt sandbox tracking not yet implemented"

    def _titanium_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Titanium Logistics (API onboarding required)
        _logger.info("Titanium sandbox tracking called for %s", tracking_number)
        return "Titanium Logistics sandbox tracking not yet implemented"

    def _pitt_ohio_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Pitt Ohio via AfterShip → https://www.aftership.com/carriers/pitt-ohio/api
        _logger.info("Pitt Ohio sandbox tracking called for %s", tracking_number)
        return "Pitt Ohio sandbox tracking not yet implemented"

    def _ceva_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: CEVA via AfterShip → https://www.aftership.com/carriers/ceva/api
        _logger.info("CEVA sandbox tracking called for %s", tracking_number)
        return "CEVA sandbox tracking not yet implemented"

    def _tforce_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: TForce via AfterShip → https://www.aftership.com/carriers/tforce/api
        _logger.info("TForce sandbox tracking called for %s", tracking_number)
        return "TForce sandbox tracking not yet implemented"

    def _tst_overland_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: TST Overland via AfterShip → https://www.aftership.com/carriers/tst-overland/api
        _logger.info("TST Overland sandbox tracking called for %s", tracking_number)
        return "TST Overland sandbox tracking not yet implemented"

    def _efw_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: EFW via AfterShip → https://www.aftership.com/carriers/efw/api
        _logger.info("EFW sandbox tracking called for %s", tracking_number)
        return "EFW sandbox tracking not yet implemented"

    def _abf_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: ABF via AfterShip → https://www.aftership.com/carriers/abf/api
        _logger.info("ABF sandbox tracking called for %s", tracking_number)
        return "ABF sandbox tracking not yet implemented"

    def _wgd_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: WGD Midwest via AfterShip → https://www.aftership.com/carriers/wgd/api
        _logger.info("WGD Midwest sandbox tracking called for %s", tracking_number)
        return "WGD Midwest sandbox tracking not yet implemented"

    def _aduie_pyle_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: A Duie Pyle (API onboarding required)
        _logger.info("A Duie Pyle sandbox tracking called for %s", tracking_number)
        return "A Duie Pyle sandbox tracking not yet implemented"

    def _saia_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Saia Motor Freight (API onboarding required)
        _logger.info("Saia sandbox tracking called for %s", tracking_number)
        return "Saia sandbox tracking not yet implemented"

    def _ch_robinson_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: C.H. Robinson (API onboarding required / TMS)
        _logger.info("C.H. Robinson sandbox tracking called for %s", tracking_number)
        return "C.H. Robinson sandbox tracking not yet implemented"

    def _ait_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: AIT Worldwide (API onboarding required)
        _logger.info("AIT Worldwide sandbox tracking called for %s", tracking_number)
        return "AIT Worldwide sandbox tracking not yet implemented"

    def _frontline_track_shipment(self, tracking_number):
        self.ensure_one()
        # TODO: Frontline Carrier Systems USA Inc (API onboarding required)
        _logger.info("Frontline sandbox tracking called for %s", tracking_number)
        return "Frontline sandbox tracking not yet implemented"

    # ────────────────────────────────────────────────────────── Test connection
    def action_test_tracking_connection(self):
        self.ensure_one()
        if not self.tracking_integration_enabled:
            raise UserError(_("Enable Tracking Integration first."))

        if self.tracking_carrier == "fedex":
            try:
                token = self._fedex_get_access_token()
                if token:
                    raise UserError(_("FedEx connection successful ✅"))
            except Exception as e:
                raise UserError(_("FedEx connection failed: %s") % str(e))

        elif self.tracking_carrier == "ups":
            # Placeholder until real UPS logic is added
            raise UserError(_("UPS test connection placeholder ✅"))

        else:
            # Generic placeholder for all other carriers for now
            raise UserError(_("%s test connection placeholder ✅") % (self.tracking_carrier or "").upper())
