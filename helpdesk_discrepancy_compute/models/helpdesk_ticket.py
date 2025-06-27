from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Re-define discrepancy field with compute and currency
    x_studio_discrepancy = fields.Monetary(
        string='Discrepancy',
        compute='_compute_x_studio_discrepancy',
        currency_field='x_studio_currency_id',
        store=True
    )

    @api.depends('x_studio_charged_amount', 'x_studio_monetary_field_782_1iumcjho4')
    def _compute_x_studio_discrepancy(self):
        for rec in self:
            charged = rec.x_studio_charged_amount or 0.0
            processed = rec.x_studio_monetary_field_782_1iumcjho4 or 0.0
            rec.x_studio_discrepancy = charged - processed
