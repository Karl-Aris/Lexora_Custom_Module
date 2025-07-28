from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute="_compute_vendor_bill_count")

    def action_create_vendor_bill(self):
        self.ensure_one()
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.name,
            'invoice_date': fields.Date.context_today(self),
            'ref': self.client_order_ref,
            'sale_order_id': self.id,
            'x_po_vb_id': self.purchase_order,  # Ensure this field exists
        })
        return {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'target': 'new',
        }
