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
        for rec in self:
            count = 0
            label = "❌ No Vendor Bill Found"
            if rec.purchase_order:
                count = self.env['account.move'].search_count([
                    ('move_type', '=', 'in_invoice'),
                    ('ref', '=', rec.purchase_order.strip())
                ])
                if count > 0:
                    label = _("View Vendor Bills (%s)") % count
            rec.vendor_bill_count = count
            rec.vendor_bill_button_label = label

    def action_open_vendor_bills(self):
        self.ensure_one()
        if not self.purchase_order:
            raise UserError(_("No PO Number on this Sales Order."))

        bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('ref', '=', self.purchase_order.strip())
        ])

        if not bills:
            raise UserError(_("No Vendor Bills found for PO: %s") % self.purchase_order.strip())

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Related Vendor Bills'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bills.ids)],
        }
        if len(bills) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': bills.id
            })
        return action
