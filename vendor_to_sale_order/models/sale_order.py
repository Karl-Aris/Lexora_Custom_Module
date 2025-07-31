from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_count = fields.Integer(compute="_compute_vendor_bill_count", string="Vendor Bill Count")

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = self.env['account.move'].search_count([
                ('sale_order_id', '=', order.id),
                ('move_type', '=', 'in_invoice')
            ])

    def action_create_vendor_bill(self):
        self.ensure_one()
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.name,
            'invoice_date': fields.Date.context_today(self),
            'ref': self.client_order_ref,
            'sale_order_id': self.id,
            'x_po_vb_id': self.purchase_order,
            'partner_id': self.partner_id.id,  # optional, but recommended
        })
        return {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'target': 'new',  # 👈 makes it a modal popup
        }
    
