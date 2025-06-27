from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_charged_amount = fields.Float(string='Charged Amount')
    x_studio_monetary_field_782_1iumcjho4 = fields.Float(string='Vendor Bill Total', readonly=True)

    discrepancy_amount = fields.Float(
        string='Discrepancy',
        compute='_compute_discrepancy_amount',
        store=True
    )

    @api.depends('x_studio_charged_amount', 'x_studio_monetary_field_782_1iumcjho4')
    def _compute_discrepancy_amount(self):
        for rec in self:
            rec.discrepancy_amount = (
                (rec.x_studio_charged_amount or 0.0) -
                (rec.x_studio_monetary_field_782_1iumcjho4 or 0.0)
            )