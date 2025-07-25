from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'x_sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )

    def action_create_vendor_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Vendor Bill'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_move_type': 'in_invoice',
                'default_x_sale_order_id': self.id,
                'default_company_id': self.company_id.id,
            }
        }
