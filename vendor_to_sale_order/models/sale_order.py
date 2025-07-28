from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_vendor_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Vendor Bill',
            'res_model': 'account.move',
            'view_mode': 'form',
            'context': {
                'default_move_type': 'in_invoice',
                'default_invoice_origin': self.name,
                'default_sale_order_id': self.id,
            },
            'target': 'current',
        }
