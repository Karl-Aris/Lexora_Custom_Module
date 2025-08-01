from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_po_number = fields.Char(
        string='PO Number',
        compute='_compute_sale_po_number',
        store=True
    )

    def _compute_sale_po_number(self):
        for record in self:
            if record.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', record.invoice_origin)], limit=1)
                record.sale_po_number = sale_order.client_order_ref or ''
            else:
                record.sale_po_number = ''
