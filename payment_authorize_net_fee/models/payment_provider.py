from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_provider_code = fields.Selection(
        selection_add=[('authorize', 'Authorize.Net')],
        string='Payment Provider',
        help='Payment method selected for this order'
    )
