from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', string="Related Sale Order")
    x_po_vb_id = fields.Char(string="PO# from Sale Order")

    sale_order_count = fields.Integer(
        string='Sale Order',
        compute='_compute_sale_order_count',
        readonly=True
    )

    @api.depends('sale_order_id')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = 1 if record.sale_order_id else 0

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.move_type == 'in_invoice' and record.x_po_vb_id and not record.sale_order_id:
                sale_order = self.env['sale.order'].search([
                    ('purchase_order', '=', record.x_po_vb_id)
                ], limit=1)
                if sale_order:
                    record.sale_order_id = sale_order.id
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            if (
                record.move_type == 'in_invoice'
                and not record.sale_order_id
                and (vals.get('x_po_vb_id') or record.x_po_vb_id)
            ):
                sale_order = self.env['sale.order'].search([
                    ('purchase_order', '=', vals.get('x_po_vb_id') or record.x_po_vb_id)
                ], limit=1)
                if sale_order:
                    record.sale_order_id = sale_order.id
        return result

    def action_view_related_sale_order(self):
        self.ensure_one()
        if not self.sale_order_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
        }
