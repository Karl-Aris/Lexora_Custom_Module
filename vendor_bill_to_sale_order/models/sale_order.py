from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')

    def _compute_vendor_bill_count(self):
        for order in self:
            order.x_vendor_bill_count = self.env['account.move'].search_count([
                ('invoice_origin', '=', order.name),
                ('move_type', '=', 'in_invoice'),
            ])

    def action_create_vendor_bill(self):
        self.ensure_one()

        ctx = {
            'default_move_type': 'in_invoice',  # Indicates Vendor Bill
            'default_invoice_origin': self.name,
            'default_partner_id': self.partner_id.id,
            'default_invoice_date': fields.Date.context_today(self),
        }

        return {
            'name': 'Create Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',  # Opens in a modal
            'context': ctx,
        }
