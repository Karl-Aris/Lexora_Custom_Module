from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many('account.move', 'sale_order_id', string="Vendor Bills", domain=[('move_type', '=', 'in_invoice')])
    vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')

    @api.depends('vendor_bill_ids')
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
            'context': {
                'default_sale_order_id': self.id,
                'default_purchase_reference': self.client_order_ref,
            }
        }
