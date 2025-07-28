from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_create_vendor_bill(self):
        # Example logic — you should replace this with your real implementation
        vendor_bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': 'Generated from Sale Order',
                'quantity': 1,
                'price_unit': 0.0,
            })],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': vendor_bill.id,
            'target': 'current',
        }
