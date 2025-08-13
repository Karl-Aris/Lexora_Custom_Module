from datetime import date
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Core fields for the workflow on Sales Orders
    x_tracking_number = fields.Char(
        string="Tracking Number",
        copy=False,
        help="Carrier tracking number as booked at shipment time."
    )
    x_edd = fields.Date(
        string="Estimated Delivery Date (EDD)",
        copy=False,
        index=True,
        help="Expected delivery date provided by the carrier or ops."
    )
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
    x_followup_status = fields.Selection(
        selection=[("pending", "Pending"), ("done", "Done")],
        string="Follow-up Status",
        copy=False,
        index=True,
        help="Use after a Delivered status to track customer follow-up."
    )

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _message_on_status_change(self, old_status, new_status):
        if old_status != new_status:
            self.message_post(
                body=_("Delivery Status changed: %s → %s") % (
                    dict(self._fields['x_delivery_status'].selection).get(old_status, old_status or "—"),
                    dict(self._fields['x_delivery_status'].selection).get(new_status, new_status or "—"),
                )
            )

    def _maybe_default_shipped_on_tracking(self, vals_by_id=None):
        """
        If tracking is newly set and status is empty, default to 'shipped'.
        `vals_by_id` is an optional dict {record.id: vals} to detect new tracking set via write.
        """
        for rec in self:
            prev_vals = (vals_by_id or {}).get(rec.id, {})
            tracking_changed = ("x_tracking_number" in prev_vals)
            if (tracking_changed and prev_vals.get("x_tracking_number")) or (not prev_vals and rec.x_tracking_number):
                if not rec.x_delivery_status:
                    old = rec.x_delivery_status
                    rec.x_delivery_status = "shipped"
                    self._message_on_status_change(old, rec.x_delivery_status)

    # ---------------------------------------------------------------------
    # Create/Write overrides
    # ---------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order, vals in zip(orders, vals_list):
            # Auto-default shipped when tracking is added on create
            if vals.get("x_tracking_number") and not vals.get("x_delivery_status"):
                old = order.x_delivery_status
                order.x_delivery_status = "shipped"
                order._message_on_status_change(old, order.x_delivery_status)
        return orders

    def write(self, vals):
        # Snapshot old statuses for chatter + detect tracking change
        old_status_map = {o.id: o.x_delivery_status for o in self}
        res = super().write(vals)

        # If tracking number was set via this write, maybe default to 'shipped'
        if "x_tracking_number" in vals:
            self._maybe_default_shipped_on_tracking({r.id: vals for r in self})

        # Log delivery status changes, manage follow-up default
        if "x_delivery_status" in vals:
            for rec in self:
                rec._message_on_status_change(old_status_map.get(rec.id), rec.x_delivery_status)
                if rec.x_delivery_status == "delivered" and not rec.x_followup_status:
                    rec.x_followup_status = "pending"
        return res

    # ---------------------------------------------------------------------
    # Cron: Auto-bucket missed EDD (daily)
    # ---------------------------------------------------------------------
    @api.model
    def cron_autobucket_missed_edd(self):
        """
        Daily:
        - Find orders with delivery_status = shipped and EDD <= today
        - Set delivery_status = not_delivered_on_edd
        """
        today = date.today()
        domain = [
            ("x_delivery_status", "=", "shipped"),
            ("x_edd", "!=", False),
            ("x_edd", "<=", today),
        ]
        orders = self.sudo().search(domain)
        for o in orders:
            old = o.x_delivery_status
            o.sudo().write({"x_delivery_status": "not_delivered_on_edd"})
            o._message_on_status_change(old, o.x_delivery_status)

    # ---------------------------------------------------------------------
    # Optional (stub): Carrier API refinement
    # ---------------------------------------------------------------------
    def _check_carrier_status_via_api(self):
        """
        Placeholder if you later wire to a carrier API using x_tracking_number.
        Return one of: 'in_transit', 'delivered', 'exception', or None.
        """
        self.ensure_one()
        return None

    @api.model
    def cron_refine_status_via_api(self):
        """
        Optional (disabled cron by default):
        - For orders in shipped or not_delivered_on_edd, call API and update.
        """
        domain = [("x_delivery_status", "in", ["shipped", "not_delivered_on_edd"]), ("x_tracking_number", "!=", False)]
        for o in self.sudo().search(domain):
            new_status = o._check_carrier_status_via_api()
            if new_status and new_status != o.x_delivery_status:
                vals = {"x_delivery_status": new_status}
                if new_status == "delivered" and not o.x_followup_status:
                    vals["x_followup_status"] = "pending"
                old = o.x_delivery_status
                o.sudo().write(vals)
                o._message_on_status_change(old, o.x_delivery_status)
