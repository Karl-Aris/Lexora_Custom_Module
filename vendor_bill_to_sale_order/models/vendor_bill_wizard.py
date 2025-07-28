from odoo import models, fields, api

class CreateVendorBillWizard(models.TransientModel):
    _name = 'create.vendor.bill.wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    purchase_reference = fields.Char("PO#")
    partner_id = fields.Many2one('res.partner', string="Vendor")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")

    def action_create_vendor_bill(self):
        self.ensure_one()
        vendor_bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.purchase_reference,
            'partner_id': self.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'quantity': self.quantity,
                'price_unit': self.price_unit,
                'name': self.product_id.name,
            })],
            'ref': self.sale_order_id.name,
        })

        # link it to sale order using a custom field if needed
        self.sale_order_id.write({'x_vendor_bill_ids': [(4, vendor_bill.id)]})

        return {'type': 'ir.actions.act_window_close'}
