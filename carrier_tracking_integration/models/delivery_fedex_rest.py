import logging
import requests
import time
import uuid

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("fedex_rest", "FedEx REST")],
        ondelete={"fedex_rest": "set default"},
    )

    fedex_client_id = fields.Char("FedEx Client ID")
    fedex_client_secret = fields.Char("FedEx Client Secret")
    fedex_use_sandbox = fields.Boolean("Use Sandbox", default=True)

    # Class-level cache
    _fedex_token_cache = None
    _token_expiry_time_cache = None

    def _get_fedex_base_url(self):
        return "https://apis-sandbox.fedex.com" if self.fedex_use_sandbox else "https://apis.fedex.com"

    def _get_fedex_token(self):
        """Fetch FedEx OAuth token (cached)."""
        if DeliveryCarrier._fedex_token_cache and time.time() < DeliveryCarrier._token_expiry_time_cache:
            return DeliveryCarrier._fedex_token_cache

        url = f"{self._get_fedex_base_url()}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.fedex_client_id,
            "client_secret": self.fedex_client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=25)
            _logger.info("FedEx Token Response: %s", response.text)

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                if token:
                    DeliveryCarrier._fedex_token_cache = token
                    DeliveryCarrier._token_expiry_time_cache = time.time() + expires_in
                    return token
            raise UserError(_("FedEx token request failed: %s") % response.text)
        except requests.exceptions.RequestException as e:
            raise UserError(_("FedEx token request error: %s") % str(e))
