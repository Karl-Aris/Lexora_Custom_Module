from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_count = fields.Integer(
        string="Sale Order Count",
        compute="_compute_sale_order_count"
    )

    sale_order_button_label = fields.Char(
        compute="_compute_sale_order_count"
    )

    def _compute_sale_order_count(self):
        for rec in self:
            count = 0
            label = "❌ No Sale Order Found"
            if rec.x_po:
                count = self.env['sale.order'].search_count([
                    ('purchase_order', '=', rec.x_po.strip())
                ])
                if count > 0:
                    label = _("View Sales Orders (%s)") % count
            rec.sale_order_count = count
            rec.sale_order_button_label = label

    def action_open_sale_order(self):
        self.ensure_one()
        if not self.x_po:
            raise UserError(_("No PO Number on this Vendor Bill."))

        orders = self.env['sale.order'].search([
            ('purchase_order', '=', self.x_po.strip())
        ])

        if not orders:
            raise UserError(_("No Sale Orders found for PO: %s") % self.x_po.strip())

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Related Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', orders.ids)],
        }
        if len(orders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': orders.id
            })
        return action
