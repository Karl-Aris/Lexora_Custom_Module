from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    authorize_net_surcharge_amount = fields.Monetary(
        string="Authorize.Net Surcharge Amount",
        compute='_compute_authorize_net_surcharge',
        store=True,
    )

    @api.depends('amount_total', 'payment_provider_code')
    def _compute_authorize_net_surcharge(self):
        for order in self:
            if order.payment_provider_code == 'authorize':
                order.authorize_net_surcharge_amount = order.amount_total * 0.035
            else:
                order.authorize_net_surcharge_amount = 0.0
