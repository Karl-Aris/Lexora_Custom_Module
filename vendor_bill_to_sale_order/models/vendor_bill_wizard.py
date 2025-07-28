# models/vendor_bill_wizard.py
from odoo import models, fields, api

class VendorBillWizard(models.TransientModel):
    _name = 'vendor.bill.wizard'
    _description = 'Vendor Bill Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    purchase_order_ref = fields.Char(string="PO#", related='sale_order_id.client_order_ref', readonly=True)

    def create_vendor_bill(self):
        vendor_bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.sale_order_id.name,
            'invoice_payment_ref': self.purchase_order_ref,
        })
        self.sale_order_id.x_vendor_bill_ids = [(4, vendor_bill.id)]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': vendor_bill.id,
            'view_mode': 'form',
            'target': 'current',
        }
