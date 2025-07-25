from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')],
    )

    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {
                'default_move_type': 'in_invoice',
                'default_sale_order_id': self.id,
            },
        }
