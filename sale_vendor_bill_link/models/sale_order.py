from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'sale_order_id',
        string='Linked Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )

    def action_view_vendor_bills(self):
        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {
                'default_sale_order_id': self.id,
                'default_move_type': 'in_invoice',
            }
        }
