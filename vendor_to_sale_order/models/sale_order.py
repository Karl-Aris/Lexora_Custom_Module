from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_id = fields.Many2one(
        'account.move',
        string="Linked Vendor Bill",
        domain="[('move_type', '=', 'in_invoice')]"
    )

    vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute="_compute_vendor_bill_count")

    def _compute_vendor_bill_count(self):
        for order in self:
            count = self.env['account.move'].search_count([
                ('sale_order_id', '=', order.id),
                ('move_type', '=', 'in_invoice')
            ])
            order.vendor_bill_count = count

    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id), ('move_type', '=', 'in_invoice')],
            'context': {'default_sale_order_id': self.id},
        }
