# models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_vendor_bill_ids = fields.Many2many('account.move', string="Vendor Bills")
    x_vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')

    def _compute_vendor_bill_count(self):
        for order in self:
            order.x_vendor_bill_count = len(order.x_vendor_bill_ids)

    def action_create_vendor_bill(self):
        return {
            'name': 'Create Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.bill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }
