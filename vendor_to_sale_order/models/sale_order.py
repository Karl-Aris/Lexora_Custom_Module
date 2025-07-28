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
            bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_origin', '=', order.name)
            ])
            count = len(bills)
            order.vendor_bill_count = count
            if count:
                order.vendor_bill_button_label = _("View Vendor Bills (%s)") % count
            else:
                order.vendor_bill_button_label = _("❌ No Vendor Bill Found")

    def action_open_vendor_bills(self):
        self.ensure_one()
        bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('invoice_origin', '=', self.name)
        ])

        if not bills:
            raise UserError(_("No Vendor Bills found for this Sales Order."))

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bills'),
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
