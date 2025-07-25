from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )

    def action_view_vendor_bills(self):
        self.ensure_one()
        form_view = self.env.ref('account.view_move_form')  # Full vendor bill form

        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {
                'default_move_type': 'in_invoice',
                'default_sale_order_id': self.id,
            },
            'target': 'current'
        }
