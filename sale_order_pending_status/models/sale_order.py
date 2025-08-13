from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status = fields.Selection(
        selection_add=[('pending', 'Pending')],
        ondelete={'pending': 'set default'}
    )
