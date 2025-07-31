from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', string='Linked Sale Order', ondelete='set null')
    x_po_vb_id = fields.Char(string="PO # (Vendor Bill)")

    @api.onchange('x_po_vb_id')
    def _onchange_x_po_vb_id(self):
        if self.move_type == 'in_invoice' and self.x_po_vb_id:
            sale_order = self.env['sale.order'].search([('x_po_so_id', '=', self.x_po_vb_id)], limit=1)
            self.sale_order_id = sale_order if sale_order else False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.move_type == 'in_invoice' and record.x_po_vb_id and not record.sale_order_id:
                so = self.env['sale.order'].search([('x_po_so_id', '=', record.x_po_vb_id)], limit=1)
                record.sale_order_id = so if so else False
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.move_type == 'in_invoice' and rec.x_po_vb_id and not rec.sale_order_id:
                so = self.env['sale.order'].search([('x_po_so_id', '=', rec.x_po_vb_id)], limit=1)
                rec.sale_order_id = so if so else False
        return res
