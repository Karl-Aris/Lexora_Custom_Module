from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        domain="[('move_type', '=', 'in_invoice'), ('state', '!=', 'cancel')]",
        help="Manually link a vendor bill to this sale order.",
        ondelete='set null'
    )
