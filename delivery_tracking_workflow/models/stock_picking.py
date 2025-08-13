from odoo import api, fields, models, _
from datetime import date

class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_delivery_status = fields.Selection(
        selection=[
            ("shipped", "Shipped"),
            ("in_transit", "In Transit"),
            ("delivered", "Delivered"),
            ("not_delivered_on_edd", "Not Delivered on EDD"),
            ("exception", "Exception"),
        ],
        string="Delivery Status",
        tracking=True,
        copy=False,
        index=True,
    )

    x_edd = fields.Date(
        string="Estimated Delivery Date (EDD)",
        copy=False,
        index=True,
        help="Expected delivery date provided by carrier or ops team."
    )

    x_followup_status = fields.Selection(
        selection=[("pending", "Pending"), ("done", "Done")],
        string="Follow-up Status",
        default=False,
        copy=False,
        index=True,
        help="Used for customer follow-up after delivery confirmation."
    )

    # -- Helpers -------------------------------------------------------------

    def _message_on_status_change(self, old_status, new_status):
        if old_status != new_status:
            self.message_post(
                body=_("Delivery Status changed: %s → %s") % (
                    dict(self._fields['x_delivery_status'].selection).get(old_status, old_status or "—"),
                    dict(self._fields['x_delivery_status'].selection).get(new_status, new_status or "—"),
                )
            )

    # -- Defaulting 'Shipped' when tracking is added ------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            # If tracking number or carrier set, mark as Shipped when unset
            if (vals.get("carrier_tracking_ref") or vals.get("carrier_id")) and not vals.get("x_delivery_status"):
                old = rec.x_delivery_status
                rec.x_delivery_status = "shipped"
                rec._message_on_status_change(old, rec.x_delivery_status)
        return records

    def write(self, vals):
        # Capture old statuses to log
        old_status_map = {r.id: r.x_delivery_status for r in self}
        res = super().write(vals)

        # If tracking number just got set and no status yet → 'shipped'
        if "carrier_tracking_ref" in vals or "carrier_id" in vals:
            for rec in self:
                if not old_status_map.get(rec.id) and rec.carrier_tracking_ref and not rec.x_delivery_status:
                    old = old_status_map.get(rec.id)
                    rec.x_delivery_status = "shipped"
                    rec._message_on_status_change(old, rec.x_delivery_status)

        # Log any explicit delivery status change and prepare follow-up toggle
        if "x_delivery_status" in vals:
            for rec in self:
                rec._message_on_status_change(old_status_map.get(rec.id), rec.x_delivery_status)
                # If just delivered, prepare follow-up status if empty
                if rec.x_delivery_status == "delivered" and not rec.x_followup_status:
                    rec.x_followup_status = "pending"
        return res

    # -- Server/Cron: Auto-bucket missed EDD --------------------------------
    @api.model
    def cron_autobucket_missed_edd(self):
        """
        Runs daily:
        - Find pickings with status = shipped and EDD <= today
        - Move them to 'not_delivered_on_edd'
        (Later: call carrier API to refine to in_transit / delivered)
        """
        today = date.today()
        domain = [
            ("x_delivery_status", "=", "shipped"),
            ("x_edd", "!=", False),
            ("x_edd", "<=", today),
        ]
        pickings = self.sudo().search(domain)
        if not pickings:
            return

        for p in pickings:
            old = p.x_delivery_status
            p.sudo().write({"x_delivery_status": "not_delivered_on_edd"})
            p._message_on_status_change(old, p.x_delivery_status)

    # -- Optional: stubs for future carrier API checks ----------------------
    def _check_carrier_status_via_api(self):
        """
        Placeholder for later:
        - Call carrier API using p.carrier_tracking_ref
        - Return one of: 'in_transit', 'delivered', 'exception', or None
        """
        self.ensure_one()
        # Implement per carrier (UPS/FedEx/DHL/etc.). Keep simple for now.
        return None

    @api.model
    def cron_refine_status_via_api(self):
        """
        Optional later:
        - For pickings with shipped or not_delivered_on_edd,
          ask the carrier API and set to in_transit/delivered/exception.
        """
        domain = [("x_delivery_status", "in", ["shipped", "not_delivered_on_edd"])]
        for p in self.sudo().search(domain):
            new_status = p._check_carrier_status_via_api()
            if new_status and new_status != p.x_delivery_status:
                old = p.x_delivery_status
                vals = {"x_delivery_status": new_status}
                # When delivered via API, mark follow-up pending if unset
                if new_status == "delivered" and not p.x_followup_status:
                    vals["x_followup_status"] = "pending"
                p.sudo().write(vals)
                p._message_on_status_change(old, p.x_delivery_status)
