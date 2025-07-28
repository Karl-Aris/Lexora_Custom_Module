from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_vendor_bill(self):
        self.ensure_one()
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.name,
            'invoice_date': fields.Date.context_today(self),
            'ref': self.client_order_ref,
            'invoice_line_ids': [],
            'sale_order_id': self.id,
        })
        return {
            'name': 'Vendor Bill',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': bill.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
