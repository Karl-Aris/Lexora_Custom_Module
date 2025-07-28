from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    vendor_bill_count = fields.Integer(
        string="Vendor Bill Count",
        compute="_compute_vendor_bill_count"
    )

    vendor_bill_button_label = fields.Char(
        compute="_compute_vendor_bill_count"
    )

    def _compute_vendor_bill_count(self):
        for order in self:
            count = self.env['account.move'].search_count([
                ('move_type', '=', 'in_invoice'),
                ('invoice_origin', '=', order.purchase_order)
            ])
            label = _("Vendor Bills (%s)") % count if count else _("❌ No Vendor Bill Found")
            order.vendor_bill_count = count
            order.vendor_bill_button_label = label

    def action_open_vendor_bills(self):
        self.ensure_one()
        if not self.purchase_order:
            raise UserError(_("No PO Number set for this Sales Order."))

        bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('invoice_origin', '=', self.purchase_order)
        ])
        if not bills:
            raise UserError(_("No Vendor Bills found for PO: %s") % self.purchase_order)

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Related Vendor Bills'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bills.ids)],
        }
        if len(bills) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = bills.id
        return action
