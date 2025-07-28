from odoo import models, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order = fields.Char(string="PO Number")  # Ensure this is present on SO as well

    def action_create_vendor_bill(self):
        self.ensure_one()

        # Pick a random expense account just for demonstration
        expense_account = self.env['account.account'].search([
            ('user_type_id.type', '=', 'expense')
        ], limit=1)

        if not expense_account:
            raise UserError(_("No expense account found to create invoice line."))

        bill = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_origin': self.name,
            'purchase_order': self.purchase_order,
            'invoice_line_ids': [(0, 0, {
                'name': 'Auto-generated from Sales Order %s' % self.name,
                'quantity': 1,
                'price_unit': self.amount_total,
                'account_id': expense_account.id,
            })],
        })

        return {
            'name': 'Vendor Bill',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': bill.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
