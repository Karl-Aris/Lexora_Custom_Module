from odoo import models, fields, api

class CreateVendorBillWizard(models.TransientModel):
    _name = 'create.vendor.bill.wizard'
    _description = 'Create Vendor Bill Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    purchase_reference = fields.Char(string="PO#", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    product_id = fields.Many2one('product.product', string="Product")
    price_unit = fields.Float(string="Unit Price")
    quantity = fields.Float(string="Quantity", default=1.0)

    def action_create_vendor_bill(self):
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.sale_order_id.name,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'price_unit': self.price_unit,
                'quantity': self.quantity,
                'name': self.product_id.name,
                'account_id': self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id,
            })],
            'sale_order_id': self.sale_order_id.id,
            'ref': self.purchase_reference,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }
