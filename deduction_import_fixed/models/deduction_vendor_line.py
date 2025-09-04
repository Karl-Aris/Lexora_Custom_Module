from odoo import models, fields

class DeductionVendorLine(models.Model):
    _name = "deduction.vendor.line"
    _description = "Deduction Vendor Line"

    deduction_id = fields.Many2one("deduction.vendor", string="Deduction Reference", ondelete="cascade", required=True)
    sku_id = fields.Many2one("product.product", string="SKU")
    po_number = fields.Char(string="PO Number")
    external_sku = fields.Char(string="External SKU")

    amount = fields.Float(string="Amount")
    cogs = fields.Float(string="COGS")

    CONDITION_SELECTION = [
        ("new", "New"),
        ("used", "Used"),
        ("refurbished", "Refurbished")
    ]
    condition = fields.Selection(CONDITION_SELECTION, string="Condition")

    # Standard fields
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    create_date = fields.Datetime(string="Created on", readonly=True)
    create_uid = fields.Many2one("res.users", string="Created by", readonly=True)
    write_date = fields.Datetime(string="Last Updated on", readonly=True)
    write_uid = fields.Many2one("res.users", string="Last Updated by", readonly=True)

    def _compute_display_name(self):
        for rec in self:
            if rec.sku_id:
                rec.display_name = rec.sku_id.display_name
            else:
                rec.display_name = rec.po_number or '-'
