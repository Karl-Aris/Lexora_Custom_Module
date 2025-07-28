from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute='_compute_vendor_bill_count')

    def _compute_vendor_bill_count(self):
        for order in self:
            # Change the domain if you track vendor bills another way
            bills = self.env['account.move'].search([
                ('invoice_origin', '=', order.name),
                ('move_type', '=', 'in_invoice')  # Vendor Bills only
            ])
            order.x_vendor_bill_count = len(bills)

    def action_create_vendor_bill(self):
        # Sample logic: redirect to bill creation window
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['context'] = {
            'default_invoice_origin': self.name,
            'default_move_type': 'in_invoice',  # Vendor Bill
            'default_partner_id': self.partner_id.id,
            'default_invoice_date': fields.Date.context_today(self),
        }
        return action
