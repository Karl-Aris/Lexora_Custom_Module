from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status = fields.Selection(
        selection=[
            ("not_delivered", "Not Delivered"),
            ("delivered", "Delivered"),
            ("exception", "Exception"),
        ],
        string="Delivery Status",
        help="Overall delivery outcome for the order.",
    )

    etd = fields.Date(
        string="Estimated Time of Delivery (ETD)",
        help="Estimated delivery date based on carrier information.",
    )

    follow_up_required = fields.Boolean(
        string="Follow-Up Required",
        help="Enable when this order needs extra tracking or intervention.",
    )

    actual_delivery_date = fields.Date(
        string="Actual Delivery Date",
        help="Fill when the order is confirmed delivered.",
    )

    contacted = fields.Selection(
        selection=[
            ("received_good", "Received Good"),
            ("received_damaged", "Received Damaged"),
            ("other", "Other"),
        ],
        string="Contacted",
        help="Contact outcome with the customer after delivery.",
    )

    contact_notes = fields.Text(
        string="Contact Notes",
        help="Notes from contacting the customer (e.g., damages, returns, feedback).",
    )
