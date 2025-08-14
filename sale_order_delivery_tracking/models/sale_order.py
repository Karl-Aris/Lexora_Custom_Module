# -*- coding: utf-8 -*-
import json
import logging
from datetime import date

import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # ---- Core tracking fields (no defaults; start blank) ----
    carrier_code = fields.Selection([
        ("fedex", "FedEx"),
        ("ups", "UPS"),
        ("usps", "USPS"),
        ("dhl", "DHL"),
    ], string="Carrier", default=False)

    tracking_number = fields.Char(string="Tracking Number")  # free text; you can fill or sync from picking
    estimated_delivery_date = fields.Date(string="Estimated Delivery Date")

    x_delivery_status = fields.Selection([
        ("shipped", "Shipped"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("not_delivered_edd", "Not Delivered on EDD"),
        ("exception", "Exception"),
    ], string="Delivery Status", default=False)

    follow_up_status = fields.Selection([
        ("pending", "Pending"),
        ("done", "Done"),
    ], string="Follow-Up Status", default=False)

    # ---- Storage for last status + full history (raw) ----
    last_tracking_status = fields.Char(string="Last Carrier Status")
    tracking_history_json = fields.Text(string="Tracking History (JSON)")

    # Optional convenience: when a picking is created/updated, you can call this to copy its tracking
    def update_tracking_from_first_picking(self):
        for order in self:
            if order.picking_ids:
                picking = order.picking_ids[0]
                if picking.carrier_tracking_ref and not order.tracking_number:
                    order.tracking_number = picking.carrier_tracking_ref

    # ---------------- Public actions ----------------
    def action_refresh_tracking_now(self):
        """
        Manual button to fetch current tracking from selected carrier and update fields/chatter.
        """
        for order in self:
            if not order.carrier_code or not order.tracking_number:
                raise UserError(_("Please set Carrier and Tracking Number before refreshing tracking."))

            try:
                status, events = order._fetch_tracking(order.carrier_code, order.tracking_number)
                order._apply_tracking_result(status, events, post_to_chatter=True)
            except UserError:
                # bubble up user-facing messages
                raise
            except Exception as e:
                _logger.exception("Tracking refresh failed for SO %s", order.name)
                raise UserError(_("Tracking refresh failed: %s") % str(e))
        return True

    @api.model
    def cron_update_tracking(self):
        """
        Daily cron to refresh tracking on orders that have a carrier + tracking number.
        You can change the search domain to narrow/focus (e.g., only open orders).
        """
        domain = [
            ("carrier_code", "!=", False),
            ("tracking_number", "!=", False),
            ("state", "not in", ["cancel"]),  # skip canceled
        ]
        orders = self.search(domain, limit=500)  # protect cron from runaway; adjust as needed
        _logger.info("Tracking cron: found %s orders to refresh", len(orders))
        for order in orders:
            try:
                status, events = order._fetch_tracking(order.carrier_code, order.tracking_number)
                order._apply_tracking_result(status, events, post_to_chatter=False)
            except Exception:
                _logger.exception("Cron: tracking refresh failed for SO %s", order.name)
        return True

    # ---------------- Private helpers ----------------
    def _apply_tracking_result(self, carrier_status: str, events: list, post_to_chatter: bool = True):
        """Map carrier status to our selection, update fields, and optionally post to chatter."""
        self.ensure_one()

        mapped = self._map_carrier_status_to_selection(carrier_status)
        write_vals = {
            "last_tracking_status": carrier_status,
            "tracking_history_json": json.dumps(events or [], default=str),
        }
        if mapped:
            write_vals["x_delivery_status"] = mapped
        self.write(write_vals)

        # Optional logic: missed EDD auto-bucket
        if self.estimated_delivery_date and self.estimated_delivery_date <= date.today():
            if (mapped in (False, "shipped", "in_transit")) and self.x_delivery_status != "delivered":
                self.x_delivery_status = "not_delivered_edd"

        if post_to_chatter:
            # Build a simple HTML history preview
            history_preview = ""
            if events:
                rows = []
                for ev in events[:10]:  # preview first 10
                    # attempt to read common keys across carriers
                    ts = ev.get("date") or ev.get("eventDateTime") or ev.get("timestamp") or ev.get("scanDateTime")
                    loc = ev.get("location") or ev.get("scanLocation") or ev.get("address") or ""
                    desc = ev.get("description") or ev.get("status") or ev.get("eventDescription") or ""
                    rows.append(f"<li><b>{ts or ''}</b> — {desc or ''} <i>{loc or ''}</i></li>")
                if rows:
                    history_preview = f"<ul>{''.join(rows)}</ul>"

            body = _(
                "Carrier: <b>%s</b><br/>Tracking #: <b>%s</b><br/>Latest: <b>%s</b>%s"
            ) % (
                dict(self._fields["carrier_code"].selection).get(self.carrier_code, self.carrier_code or ""),
                self.tracking_number or "",
                carrier_status or "",
                f"<br/>History Preview:{history_preview}" if history_preview else "",
            )
            self.message_post(body=body, subtype_xmlid="mail.mt_note")

    def _map_carrier_status_to_selection(self, carrier_status: str):
        """Normalize various carrier strings to our x_delivery_status values."""
        if not carrier_status:
            return False
        s = (carrier_status or "").strip().lower()

        # Common mappings
        table = {
            "delivered": "delivered",
        }
