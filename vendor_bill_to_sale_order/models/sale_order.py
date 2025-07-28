from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    vendor_bill_ids = fields.One2many("account.move", "sale_order_id", string="Vendor Bills")
    vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute="_compute_vendor_bill_count")

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)

    def open_create_vendor_bill_wizard(self):
        # This would normally open a wizard, placeholder action for now
        return {{
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "target": "new",
        }}
