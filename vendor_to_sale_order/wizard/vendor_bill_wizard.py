from odoo import models, fields

class VendorBillWizard(models.TransientModel):
    _name = 'vendor.bill.wizard'
    _description = 'Vendor Bill Creation Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    x_po_vb_id = fields.Char(string="PO# from Sale Order", required=True)

    def action_create_vendor_bill(self):
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.sale_order_id.name,
            'invoice_date': fields.Date.context_today(self),
            'ref': self.sale_order_id.client_order_ref,
            'sale_order_id': self.sale_order_id.id,
            'x_po_vb_id': self.x_po_vb_id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': bill.id,
            'target': 'current',
        }
