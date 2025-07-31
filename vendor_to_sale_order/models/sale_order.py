from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_po_so_id = fields.Char(string="PO # (Sale Order)")
    vendor_bill_ids = fields.One2many('account.move', 'sale_order_id', string='Vendor Bills')
    vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')

    @api.depends('vendor_bill_ids')
    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)
