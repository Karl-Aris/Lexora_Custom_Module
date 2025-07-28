from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_vendor_bill(self):
        self.ensure_one()
        bill = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_origin': self.name,
            'invoice_line_ids': [...],
        })
        return {
            'name': 'Vendor Bill',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': bill.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
