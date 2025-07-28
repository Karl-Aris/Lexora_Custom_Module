from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many('account.move', 'sale_order_id', string="Vendor Bills")
    vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)

    def open_create_vendor_bill_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Vendor Bill',
            'res_model': 'create.vendor.bill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def action_view_vendor_bills(self):
        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
        }