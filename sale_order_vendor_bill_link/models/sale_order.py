from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move',
        'sale_order_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )

    vendor_bill_count = fields.Integer(
        string='Vendor Bill Count',
        compute='_compute_vendor_bill_count'
    )

    @api.depends('vendor_bill_ids')
    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)
    
    def action_view_vendor_bills(self):
        self.ensure_one()
        vendor_bills = self.vendor_bill_ids
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
    
        if len(vendor_bills) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = vendor_bills.id
        else:
            action['domain'] = [('id', 'in', vendor_bills.ids)]
            action['views'] = [(False, 'list'), (self.env.ref('account.view_move_form').id, 'form')]
        return action
