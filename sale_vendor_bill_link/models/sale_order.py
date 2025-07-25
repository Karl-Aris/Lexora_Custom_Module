from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'x_sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )

    vendor_bill_count = fields.Integer(
        string='Vendor Bill Count',
        compute='_compute_vendor_bill_count'
    )

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)

    def action_view_vendor_bills(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bills'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
        }
        if len(self.vendor_bill_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.vendor_bill_ids.id
        return action

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
