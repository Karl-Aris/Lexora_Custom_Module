from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_ids = fields.One2many(
        comodel_name='account.move',
        compute='_compute_vendor_bill_ids',
        string='Vendor Bills',
        store=False,
    )

    @api.depends('name')
    def _compute_vendor_bill_ids(self):
        for order in self:
            order.vendor_bill_ids = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_origin', '=', order.name),
            ])
