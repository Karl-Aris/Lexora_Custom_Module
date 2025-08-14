import json
import logging
import time
from datetime import datetime, timedelta

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

FEDEX_DEFAULT_SANDBOX = "https://apis-sandbox.fedex.com"
FEDEX_DEFAULT_PROD = "https://apis.fedex.com"


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('fedex_rest', "FedEx (REST)")],
        ondelete={'fedex_rest': 'set default'}
    )

    # Auth / configuration
    fedex_rest_api_key = fields.Char("FedEx API Key (Client ID)")
    fedex_rest_api_secret = fields.Char("FedEx API Secret (Client Secret)")
    fedex_rest_account_number = fields.Char("FedEx Account Number")

    fedex_rest_base_url = fields.Char(
        "FedEx API Base URL",
        default=FEDEX_DEFAULT_SANDBOX,
        help="Sandbox: https://apis-sandbox.fedex.com, Production: https://apis.fedex.com",
    )
    fedex_rest_service_type = fields.Selection([
        ("FEDEX_GROUND", "FEDEX_GROUND"),
        ("FEDEX_2_DAY", "FEDEX_2_DAY"),
        ("FEDEX_EXPRESS_SAVER", "FEDEX_EXPRESS_SAVER"),
        ("STANDARD_OVERNIGHT", "STANDARD_OVERNIGHT"),
        ("PRIORITY_OVERNIGHT", "PRIORITY_OVERNIGHT"),
        ("INTERNATIONAL_ECONOMY", "INTERNATIONAL_ECONOMY"),
        ("INTERNATIONAL_PRIORITY", "INTERNATIONAL_PRIORITY"),
    ], string="FedEx Service Type", default="FEDEX_GROUND")

    fedex_rest_dropoff_type = fields.Selection([
        ("REGULAR_PICKUP", "REGULAR_PICKUP"),
        ("REQUEST_COURIER", "REQUEST_COURIER"),
        ("DROP_BOX", "DROP_BOX"),
        ("BUSINESS_SERVICE_CENTER", "BUSINESS_SERVICE_CENTER"),
    ], string="FedEx Drop-Off Type", default="REGULAR_PICKUP")

    fedex_rest_packaging_type = fields.Selection([
        ("YOUR_PACKAGING", "YOUR_PACKAGING"),
        ("FEDEX_BOX", "FEDEX_BOX"),
        ("FEDEX_ENVELOPE", "FEDEX_ENVELOPE"),
        ("FEDEX_PAK", "FEDEX_PAK"),
        ("FEDEX_TUBE", "FEDEX_TUBE"),
    ], string="FedEx Package Type", default="FEDEX_BOX")

    fedex_rest_label_stock_type = fields.Selection([
        ("PAPER_4X6", "PAPER_4X6"),
        ("PAPER_4X8", "PAPER_4X8"),
        ("PAPER_7X4.75", "PAPER_7X4.75"),
    ], string="Label Stock", default="PAPER_4X6")

    fedex_rest_label_image_type = fields.Selection([
        ("PDF", "PDF"),
        ("PNG", "PNG"),
        ("ZPLII", "ZPLII"),
    ], string="Label Format", default="PDF")

    fedex_rest_use_locations = fields.Boolean("Use FedEx Locations", default=False)

    # OAuth token cache (stored per carrier record)
    fedex_rest_access_token = fields.Char("FedEx Access Token", readonly=True, copy=False)
    fedex_rest_token_expiry = fields.Datetime("FedEx Token Expiry", readonly=True, copy=False)

    # ===============
    # Core overrides
    # ===============
    def rate_shipment(self, order):
        self.ensure_one()
        if self.delivery_type != "fedex_rest":
            return super().rate_shipment(order)
        try:
            payload = self._fedex_build_rate_payload_from_sale(order)
            token = self._fedex_rest_get_token()
            url = f"{self.fedex_rest_base_url.rstrip('/')}/rate/v1/rates/quotes"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            _logger.info("[FedEx REST] Rate request: %s", json.dumps(payload))
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            _logger.info("[FedEx REST] Rate response: %s", resp.text)
            if resp.status_code >= 300:
                raise UserError(_("FedEx rate error: %s") % resp.text)
            data = resp.json()
            amount = self._fedex_pick_best_rate_amount(data)
            if amount is None:
                raise UserError(_("FedEx returned no rates for this shipment."))
            # Apply margins
            price = self._get_price_available(order, amount)
            return {"success": True, "price": price, "error_message": False, "warning_message": False}
        except Exception as e:
            _logger.exception("FedEx rating failed")
            return {"success": False, "price": 0.0, "error_message": str(e), "warning_message": False}

    def send_shipping(self, pickings):
        res = []
        for picking in pickings:
            carrier = picking.carrier_id or self
            if carrier.delivery_type != "fedex_rest":
                res.append(super(DeliveryCarrier, carrier).send_shipping(picking))
                continue
            try:
                payload = carrier._fedex_build_ship_payload_from_picking(picking)
                token = carrier._fedex_rest_get_token()
                url = f"{carrier.fedex_rest_base_url.rstrip('/')}/ship/v1/shipments"
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                _logger.info("[FedEx REST] Ship request: %s", json.dumps(payload))
                resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                _logger.info("[FedEx REST] Ship response: %s", resp.text)
                if resp.status_code >= 300:
                    raise UserError(_("FedEx ship error: %s") % resp.text)
                data = resp.json()
                tracking_number, label_bytes = carrier._fedex_parse_shipment_label(data)
                if not tracking_number:
                    raise UserError(_("FedEx did not return a tracking number."))
                # Attach label to picking
                if label_bytes:
                    fname = f"FedEx_{tracking_number}.pdf" if carrier.fedex_rest_label_image_type == "PDF" else f"FedEx_{tracking_number}.png"
                    picking.message_post(attachments=[(fname, label_bytes)])
                carrier._set_tracking(picking, tracking_number)
                res.append({
                    "exact_price": 0.0,
                    "tracking_number": tracking_number,
                    "carrier_tracking_ref": tracking_number,
                })
            except Exception as e:
                _logger.exception("FedEx shipping failed")
                res.append({"exact_price": 0.0, "tracking_number": False, "error_message": str(e)})
        return res

    def get_return_label(self, pickings):
        res = []
        for picking in pickings:
            carrier = picking.carrier_id or self
            if carrier.delivery_type != "fedex_rest":
                res.append(super(DeliveryCarrier, carrier).get_return_label(picking))
                continue
            try:
                payload = carrier._fedex_build_ship_payload_from_picking(picking, is_return=True)
                token = carrier._fedex_rest_get_token()
                url = f"{carrier.fedex_rest_base_url.rstrip('/')}/ship/v1/shipments"
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                _logger.info("[FedEx REST] Return request: %s", json.dumps(payload))
                resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                _logger.info("[FedEx REST] Return response: %s", resp.text)
                if resp.status_code >= 300:
                    raise UserError(_("FedEx return label error: %s") % resp.text)
                data = resp.json()
                tracking_number, label_bytes = carrier._fedex_parse_shipment_label(data)
                if label_bytes:
                    fname = f"FedEx_RETURN_{tracking_number}.pdf" if carrier.fedex_rest_label_image_type == "PDF" else f"FedEx_RETURN_{tracking_number}.png"
                    picking.message_post(attachments=[(fname, label_bytes)])
                res.append((label_bytes, tracking_number))
            except Exception as e:
                _logger.exception("FedEx return failed")
                res.append((False, False))
        return res

    # =========================
    # Payload builders & parser
    # =========================
    def _fedex_build_rate_payload_from_sale(self, order):
        self.ensure_one()
        shipper_addr = self._fedex_from_company_address(self.env.company)
        recipient_addr = self._fedex_from_partner_address(order.partner_shipping_id)
        weight_lbs, dims = self._fedex_compute_package(order)
        payload = {
            "accountNumber": {"value": self.fedex_rest_account_number},
            "requestedShipment": {
                "shipper": {"address": shipper_addr},
                "recipient": {"address": recipient_addr},
                "pickupType": self.fedex_rest_dropoff_type,
                "serviceType": self.fedex_rest_service_type,
                "packagingType": self.fedex_rest_packaging_type,
                "rateRequestType": ["LIST", "ACCOUNT"],
                "requestedPackageLineItems": [
                    {
                        "weight": {"units": "LB", "value": max(weight_lbs, 1)},
                        "dimensions": dims,
                    }
                ],
            },
        }
        return payload

    def _fedex_build_ship_payload_from_picking(self, picking, is_return=False):
        self.ensure_one()
        company = picking.company_id or self.env.company
        shipper_partner = company.partner_id
        recipient_partner = picking.partner_id
        if is_return:
            # Swap endpoints for returns
            shipper_partner, recipient_partner = recipient_partner, shipper_partner

        shipper = self._fedex_party(shipper_partner)
        recipient = self._fedex_party(recipient_partner)

        weight_lbs, dims = self._fedex_compute_package_from_moves(picking.move_line_ids)

        payload = {
            "labelResponseOptions": "LABEL",
            "requestedShipment": {
                "shipper": shipper,
                "recipients": [recipient],
                "pickupType": self.fedex_rest_dropoff_type,
                "serviceType": self.fedex_rest_service_type,
                "packagingType": self.fedex_rest_packaging_type,
                "shippingChargesPayment": {
                    "paymentType": "SENDER" if not is_return else "RECIPIENT",
                    "payor": {
                        "responsibleParty": {
                            "accountNumber": {"value": self.fedex_rest_account_number}
                        }
                    },
                },
                "labelSpecification": {
                    "labelFormatType": "COMMON2D",
                    "imageType": self.fedex_rest_label_image_type,
                    "labelStockType": self.fedex_rest_label_stock_type,
                },
                "requestedPackageLineItems": [
                    {
                        "weight": {"units": "LB", "value": max(weight_lbs, 1)},
                        "dimensions": dims,
                    }
                ],
            },
        }
        return payload

    def _fedex_parse_shipment_label(self, data):
        """Extract tracking number and label bytes from FedEx REST ship response.
        The REST response may include either an encoded label or a label URL.
        We support both; Odoo will store the PDF/PNG as attachment.
        """
        try:
            # Tracking number
            tracking = None
            if data.get("output"):
                pkg = (data["output"].get("transactionShipments") or [{}])[0]
                if pkg.get("pieceResponses"):
                    tracking = pkg["pieceResponses"][0].get("trackingNumber")
                elif pkg.get("masterTrackingNumber"):
                    tracking = pkg.get("masterTrackingNumber")

            # Label
            label_bytes = None
            if data.get("output"):
                labels = (data["output"].get("transactionShipments") or [{}])[0].get("pieceResponses") or []
                if labels and labels[0].get("label") and labels[0]["label"].get("parts"):
                    # Parts may contain base64 content
                    parts = labels[0]["label"]["parts"]
                    # Concatenate parts if multiple (usually one)
                    import base64
                    content = b"".join(base64.b64decode(p.get("image")) for p in parts if p.get("image"))
                    label_bytes = content
            return tracking, label_bytes
        except Exception:
            _logger.exception("Failed parsing FedEx REST label response")
            return None, None

    # =================
    # Helper utilities
    # =================
    def _fedex_rest_get_token(self):
        self.ensure_one()
        now = fields.Datetime.now()
        if self.fedex_rest_access_token and self.fedex_rest_token_expiry and now < self.fedex_rest_token_expiry:
            return self.fedex_rest_access_token

        if not self.fedex_rest_api_key or not self.fedex_rest_api_secret:
            raise UserError(_("FedEx API Key/Secret are missing."))

        url = f"{self.fedex_rest_base_url.rstrip('/')}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.fedex_rest_api_key,
            "client_secret": self.fedex_rest_api_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(url, data=data, headers=headers, timeout=30)
        if resp.status_code >= 300:
            raise UserError(_("FedEx OAuth failed: %s") % resp.text)
        token_data = resp.json()
        access_token = token_data.get("access_token")
        expires_in = int(token_data.get("expires_in", 3600))
        self.write({
            "fedex_rest_access_token": access_token,
            "fedex_rest_token_expiry": fields.Datetime.now() + timedelta(seconds=expires_in - 60),
        })
        return access_token

    def _fedex_from_company_address(self, company):
        partner = company.partner_id
        return self._fedex_address_dict(partner)

    def _fedex_from_partner_address(self, partner):
        return self._fedex_address_dict(partner)

    def _fedex_address_dict(self, partner):
        state_code = partner.state_id.code if partner.state_id else None
        return {
            "streetLines": [l for l in [partner.street, partner.street2] if l] or ["N/A"],
            "city": partner.city or "",
            "stateOrProvinceCode": state_code or "",
            "postalCode": partner.zip or "",
            "countryCode": partner.country_id.code or "US",
        }

    def _fedex_contact_dict(self, partner):
        return {
            "personName": partner.name or (partner.commercial_company_name or "Odoo Partner"),
            "phoneNumber": partner.phone or "0000000000",
            "companyName": partner.commercial_company_name or partner.name or "Odoo",
        }

    def _fedex_party(self, partner):
        return {
            "contact": self._fedex_contact_dict(partner),
            "address": self._fedex_address_dict(partner),
        }

    def _fedex_compute_package(self, order):
        # Very simple consolidation: sum weights; take max dims from product packaging if present
        weight_lbs = 0.0
        max_l = max_w = max_h = 0.0
        for line in order.order_line.filtered(lambda l: not l.display_type and l.product_id):
            qty = line.product_uom_qty
            product = line.product_id
            # Convert weight to lb
            weight_lbs += (product.weight or 1.0) * qty * 2.20462  # kg -> lb if weight is in kg
            # Dimensions (fallback defaults)
            max_l = max(max_l, (product.length or 12.0))
            max_w = max(max_w, (product.width or 9.0))
            max_h = max(max_h, (product.height or 6.0))
        dims = {"length": int(max_l or 12), "width": int(max_w or 9), "height": int(max_h or 6), "units": "IN"}
        return max(weight_lbs, 1.0), dims

    def _fedex_compute_package_from_moves(self, move_lines):
        weight_lbs = 0.0
        max_l = max_w = max_h = 0.0
        for ml in move_lines:
            qty = ml.qty_done or ml.product_uom_qty or 1.0
            product = ml.product_id
            weight_lbs += (product.weight or 1.0) * qty * 2.20462
            max_l = max(max_l, (product.length or 12.0))
            max_w = max(max_w, (product.width or 9.0))
            max_h = max(max_h, (product.height or 6.0))
        dims = {"length": int(max_l or 12), "width": int(max_w or 9), "height": int(max_h or 6), "units": "IN"}
        return max(weight_lbs, 1.0), dims

    def _fedex_pick_best_rate_amount(self, rate_response):
        """Return a numeric amount from FedEx rate response.
        This chooses ACCOUNT rate if present, otherwise LIST.
        """
        try:
            rated = rate_response.get("output", {}).get("rateReplyDetails", [])
            if not rated:
                # Newer responses may put quotes in "rateReplyDetails" list inside output
                rated = rate_response.get("rateReplyDetails", [])
            # Find monetary amount in shipmentRateDetails
            for r in rated:
                details = r.get("ratedShipmentDetails") or []
                for d in details:
                    # Prefer ACCOUNT totalNetCharge
                    total = d.get("totalNetCharge") or d.get("totalBaseCharge") or {}
                    amt = total.get("amount")
                    if amt is not None:
                        return float(amt)
        except Exception:
            _logger.exception("Could not parse FedEx rate response")
        return None

    def _set_tracking(self, picking, tracking_number):
        picking.carrier_tracking_ref = tracking_number
        picking.message_post(body=_("FedEx Tracking Number: %s") % tracking_number)
