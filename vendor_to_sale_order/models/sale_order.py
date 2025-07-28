from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_count = fields.Integer(
        string="Vendor Bill Count",
        compute="_compute_vendor_bill_count",
    )

    show_create_vendor_bill = fields.Boolean(
        compute="_compute_vendor_bill_visibility", store=False
    )

    show_vendor_bill_button = fields.Boolean(
        compute="_compute_vendor_bill_visibility", store=False
    )

    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = self.env['account.move'].search_count([
                ('sale_order_id', '=', order.id),
                ('move_type', '=', 'in_invoice'),
            ])

    def _compute_vendor_bill_visibility(self):
        for order in self:
            order.show_create_vendor_bill = order.state == 'sale'
            order.show_vendor_bill_button = order.vendor_bill_count > 0

    def action_create_vendor_bill(self):
        self.ensure_one()

        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_origin': self.name,
            'invoice_date': fields.Date.context_today(self),
            'ref': self.client_order_ref,
            'sale_order_id': self.id,
            'x_po_vb_id': self.purchase_order,  # Only if this field exists
        })

        form_view = self.env.ref('account.view_move_form')  # Correct vendor bill form

        return {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'views': [(form_view.id, 'form')],
            'target': 'new',
        }
