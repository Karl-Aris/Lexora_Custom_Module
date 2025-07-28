from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute="_compute_vendor_bill_count")

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = self.env['account.move'].search_count([
                ('invoice_origin', '=', order.name),
                ('move_type', '=', 'in_invoice')
            ])

    def action_create_vendor_bill(self):
        self.ensure_one()

        vendor = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
        if not vendor:
            raise UserError("No vendor found. Please configure at least one vendor.")

        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': f"Vendor Bill from SO {self.name}",
                'quantity': 1,
                'price_unit': 0.0,
            })],
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': bill.id,
            'target': 'new',
        }
