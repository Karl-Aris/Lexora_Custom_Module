from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        'account.move', 'sale_origin_ref_id',
        string='Vendor Bills',
        compute='_compute_vendor_bill_ids',
        store=False,
    )

    def _compute_vendor_bill_ids(self):
        for order in self:
            vendor_bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_origin', '=', order.name),
            ])
            order.vendor_bill_ids = vendor_bills
