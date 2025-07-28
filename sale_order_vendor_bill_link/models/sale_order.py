from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move', 'sale_order_id', string="Vendor Bills",
        domain=[('move_type', '=', 'in_invoice')]
    )
    vendor_bill_count = fields.Integer(
        string="Vendor Bill Count", compute="_compute_vendor_bill_count", store=True
    )

    @api.depends('vendor_bill_ids')
    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)

    def action_view_vendor_bills(self):
        self.ensure_one()
        bills = self.vendor_bill_ids
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(bills) == 1:
            action['res_id'] = bills.id
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        else:
            action['domain'] = [('id', 'in', bills.ids)]
        return action
