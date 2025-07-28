from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_vendor_bill(self):
        self.ensure_one()
        return {
            'name': 'Create Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.bill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_x_po_vb_id': self.purchase_order,
            }
        }
