import json
import logging
from datetime import date

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import pdf

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    # Extend provider selection with our new type
    delivery_type = fields.Selection(selection_add=[("fedex_rest", "FedEx (REST)")])

    # FedEx REST credentials & options
    fedex_api_key = fields.Char("FedEx API Key")
    fedex_api_secret = fields.Char("FedEx API Secret")
    fedex_account_number = fields.Char("FedEx Account Number")
    fedex_use_sandbox = fields.Boolean("Use FedEx Sandbox", default=True)

    # Shipping config (keep names similar to Odoo's FedEx for familiarity)
    fedex_service_type_rest = fields.Selection([
        ("FEDEX_GROUND", "FedEx Ground"),
        ("FEDEX_EXPRESS_SAVER", "Express Saver"),
        ("FEDEX_2_DAY", "2 Day"),
        ("STANDARD_OVERNIGHT", "Standard Overnight"),
        ("PRIORITY_OVERNIGHT", "Priority Overnight"),
        ("INTERNATIONAL_PRIORITY", "International Priority"),
        ("INTERNATIONAL_ECONOMY", "International Economy"),
    ], string="FedEx Service (REST)", default="FEDEX_GROUND")

    fedex_packaging_type_rest = fields.Selection([
        ("YOUR_PACKAGING", "Your Packaging"),
        ("FEDEX_PAK", "FedEx Pak"),
        ("FEDEX_BOX", "FedEx Box"),
        ("FEDEX_TUBE", "FedEx Tube"),
        ("FEDEX_ENVELOPE", "FedEx Envelope"),
    ], string="Packaging Type", default="YOUR_PACKAGING")

    fedex_pickup_type_rest = fields.Selection([
        ("DROPOFF_AT_FEDEX_LOCATION", "Drop off at FedEx location"),
        ("USE_SCHEDULED_PICKUP", "Use scheduled pickup"),
    ], string="Pickup Type", default="DROPOFF_AT_FEDEX_LOCATION")

    fedex_label_image_type = fields.Selection([
        ("PDF", "PDF"),
        ("PNG", "PNG"),
        ("ZPLII", "ZPL II"),
    ], string="Label Image Type", default="PDF")

    fedex_label_stock_type = fields.Selection([
        ("PAPER_85X11_TOP_HALF_LABEL", "Paper 8.5x11 (Top Half)"),
        ("STOCK_4X6", "Thermal 4x6"),
    ], string="Label Stock")

    # ----------------------------
    # Public API required by Odoo
    # ----------------------------
    def rate_shipment(self, order):
        self.ensure_one()
        if self.delivery_type != "fedex_rest":
            return super().rate_shipment(order)
        try:
            quote = self._fedex_rest_rate(order)
            price = quote.get("amount", 0.0)
            return {
                "success": True,
                "price": price,
                "warning_message": False,
                "error_message": False,
            }
        except Exception as e:
            _logger.exception("FedEx REST rate error")
            return {
                "success": False,
                "price": 0.0,
                "warning_message": False,
                "error_message": str(e),
            }

    def send_shipping(self, picking):
        self.ensure_one()
        if self.delivery_type != "fedex_rest":
            return super().send_shipping(picking)
        try:
            resp = self._fedex_rest_ship(picking)
            return [resp]
        except Exception as e:
            _logger.exception("FedEx REST shipment error")
            raise UserError(str(e))

    def get_tracking_link(self, picking):
        self.ensure_one()
        if self.delivery_type != "fedex_rest":
            return super().get_tracking_link(picking)
        # FedEx universal tracking page (no API call needed)
        if picking.carrier_tracking_ref:
            return f"https://www.fedex.com/fedextrack/?trknbr={picking.carrier_tracking_ref}"
        return False

    # ---------------------------------
    # FedEx REST helpers (auth, payload)
    # ---------------------------------
    def _fedex_base_url(self):
        return "https://apis-sandbox.fedex.com" if self.fedex_use_sandbox else "https://apis.fedex.com"

    def _fedex_get_access_token(self):
        if not (self.fedex_api_key and self.fedex_api_secret):
            raise UserError(_("FedEx API Key/Secret are required."))
        url = f"{self._fedex_base_url()}/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.fedex_api_key,
            "client_secret": self.fedex_api_secret,
        }
        res = requests.post(url, headers=headers, data=data, timeout=30)
        if res.status_code != 200:
            raise UserError(_("FedEx auth failed: %s") % res.text)
        return res.json()["access_token"]

    # ------- RATING -------
    def _fedex_rest_rate(self, order):
        token = self._fedex_get_access_token()
        url = f"{self._fedex_base_url()}/rate/v1/rates/quotes"
        shipper = order.company_id.partner_id
        recipient = order.partner_shipping_id

        # Compute weight (fallback 1.0)
        weight = order._get_delivery_weight() or 1.0
        weight_uom = "KG" if (self.fedex_label_image_type != "LB") else "LB"  # simple heuristic

        payload = {
            "rateRequestControlParameters": {"returnTransitTimes": False},
            "requestedShipment": {
                "shipper": {
                    "address": self._fedex_address(shipper),
                },
                "recipient": {
                    "address": self._fedex_address(recipient),
                },
                "shipDatestamp": date.today().strftime("%Y-%m-%d"),
                "serviceType": self.fedex_service_type_rest,
                "packagingType": self.fedex_packaging_type_rest,
                "pickupType": self.fedex_pickup_type_rest,
                "requestedPackageLineItems": [
                    {
                        "weight": {"units": weight_uom, "value": float(weight)},
                        "groupPackageCount": 1,
                    }
                ],
            },
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code != 200:
            raise UserError(_("FedEx rate failed: %s") % res.text)
        data = res.json()
        # Very defensive extraction – actual field names may vary per account/region
        amount = 0.0
        try:
            shipment_rate = data["output"]["rateReplyDetails"][0]["ratedShipmentDetails"][0]["totalNetCharge"]["amount"]
            amount = float(shipment_rate)
        except Exception:
            # fall back to zero if not present
            pass
        return {"amount": amount, "raw": json.dumps(data)}

    def _fedex_address(self, partner):
        return {
            "streetLines": list(filter(None, [partner.street, partner.street2])) or [""],
            "city": partner.city or "",
            "stateOrProvinceCode": (partner.state_id and partner.state_id.code) or "",
            "postalCode": partner.zip or "",
            "countryCode": (partner.country_id and partner.country_id.code) or "",
            "residential": (not partner.is_company) or False,
        }

    # ------- SHIPPING / LABEL -------
    def _fedex_rest_ship(self, picking):
        token = self._fedex_get_access_token()
        url = f"{self._fedex_base_url()}/ship/v1/shipments"

        shipper = picking.company_id.partner_id
        recipient = picking.partner_id
        weight = picking.shipping_weight or sum(picking.move_ids.filtered(lambda m: not m.scrapped).mapped("product_uom_qty")) or 1.0

        # ask for label binary (base64) so we can attach it directly
        label_image_type = self.fedex_label_image_type or "PDF"
        label_stock_type = self.fedex_label_stock_type or "PAPER_85X11_TOP_HALF_LABEL"

        payload = {
            "labelResponseOptions": "LABEL",
            "requestedShipment": {
                "shipper": {
                    "address": self._fedex_address(shipper),
                    "contact": {
                        "personName": shipper.name or "",
                        "phoneNumber": shipper.phone or shipper.mobile or "",
                        "companyName": shipper.commercial_company_name or shipper.name or "",
                    },
                },
                "recipient": {
                    "address": self._fedex_address(recipient),
                    "contact": {
                        "personName": recipient.name or "",
                        "phoneNumber": recipient.phone or recipient.mobile or "",
                        "companyName": recipient.commercial_company_name or recipient.name or "",
                    },
                },
                "shipDatestamp": date.today().strftime("%Y-%m-%d"),
                "serviceType": self.fedex_service_type_rest,
                "packagingType": self.fedex_packaging_type_rest,
                "pickupType": self.fedex_pickup_type_rest,
                "shippingChargesPayment": {
                    "paymentType": "SENDER",
                    "payor": {
                        "responsibleParty": {
                            "accountNumber": {"value": self.fedex_account_number},
                        }
                    },
                },
                "labelSpecification": {
                    "imageType": label_image_type,
                    "labelStockType": label_stock_type,
                },
                "requestedPackageLineItems": [
                    {
                        "weight": {"units": "KG", "value": float(weight) if weight else 1.0},
                        "groupPackageCount": 1,
                    }
                ],
            },
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        res = requests.post(url, headers=headers, json=payload, timeout=120)
        if res.status_code != 200:
            raise UserError(_("FedEx ship failed: %s") % res.text)
        data = res.json()

        try:
            shipment = data["output"]["transactionShipments"][0]
            master_tracking = shipment.get("masterTrackingNumber") or shipment.get("masterTrackingId")
            piece = shipment["pieceResponses"][0]
            doc = piece["packageDocuments"][0]
            # when labelResponseOptions=LABEL, the API typically returns a base64 image under 'encodedLabel'
            label_b64 = doc.get("encodedLabel") or doc.get("content")
        except Exception as e:
            raise UserError(_("FedEx response parsing failed: %s\n%s") % (e, json.dumps(data)))

        # Attach label to picking
        filename = f"FEDEX_{picking.name}.{label_image_type.lower()}"
        self._fedex_attach_label(picking, filename, label_b64)

        # Save tracking to picking (and let Odoo propagate if needed)
        if master_tracking:
            if picking.carrier_tracking_ref:
                picking.carrier_tracking_ref += "," + master_tracking
            else:
                picking.carrier_tracking_ref = master_tracking

        # Compute price via rate API (optional). If it fails, keep zero and don't block shipment.
        exact_price = 0.0
        try:
            quote = self._fedex_rest_rate(picking.sale_id) if picking.sale_id else {"amount": 0.0}
            exact_price = float(quote.get("amount", 0.0))
        except Exception:
            pass

        # Post message
        picking.message_post(body=_("Shipment created into FedEx (REST)\nTracking: %s") % (picking.carrier_tracking_ref or "N/A"))

        return {
            "exact_price": exact_price,
            "tracking_number": picking.carrier_tracking_ref or "",
        }

    def _fedex_attach_label(self, picking, filename, label_b64):
        if not label_b64:
            return
        # If label is base64 (most APIs), store it directly. If it's a URL, you could fetch then attach.
        self.env["ir.attachment"].create({
            "name": filename,
            "res_model": picking._name,
            "res_id": picking.id,
            "type": "binary",
            "datas": label_b64,
            "mimetype": self._mimetype_from_ext(filename),
        })

    def _mimetype_from_ext(self, filename):
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            return "application/pdf"
        if ext in ("png",):
            return "image/png"
        if ext in ("zpl", "zplii"):
            return "application/octet-stream"
        return "application/octet-stream"
