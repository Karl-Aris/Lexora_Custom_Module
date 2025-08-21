# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class CarrierWebhookController(http.Controller):

    @http.route(['/webhook/carrier/<string:carrier>'], type='json', auth='public', methods=['POST'], csrf=False)
    def carrier_webhook(self, carrier, **kwargs):
        """
        Generic webhook endpoint for carriers
        Example URL: /webhook/carrier/fedex
        Expected JSON payload: { "tracking_number": "...", "status": "..." }
        """
        payload = request.jsonrequest or {}
        tracking_number = payload.get("tracking_number")
        status = payload.get("status")

        if not tracking_number:
            return {"error": "Missing tracking_number"}

        order = request.env["sale.order"].sudo().search([("tracking_number", "=", tracking_number)], limit=1)
        if not order:
            _logger.warning("Webhook %s: No order found for tracking %s", carrier, tracking_number)
            return {"error": "Order not found"}

        order.sudo().write({"tracking_status": status or "Unknown"})
        _logger.info("Webhook %s updated order %s with status: %s", carrier, order.name, status)

        return {"success": True, "order": order.name, "tracking_number": tracking_number, "status": status or "Unknown"}
