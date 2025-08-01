from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_payment_provider_code = fields.Char(string='Payment Provider Code')
