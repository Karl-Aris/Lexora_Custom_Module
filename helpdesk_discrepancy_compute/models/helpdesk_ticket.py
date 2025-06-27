from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_studio_discrepancy = fields.Monetary(
        string='Discrepancy',
        compute='_compute_discrepancy',
        currency_field='x_studio_currency_id',
        store=True
    )

    @api.depends('x_studio_charged_amount', 'x_studio_monetary_field_782_1iumcjho4')
    def _compute_discrepancy(self):
        for rec in self:
            rec.x_studio_discrepancy = (
                (getattr(rec, 'x_studio_charged_amount', 0.0) or 0.0)
                - (getattr(rec, 'x_studio_monetary_field_782_1iumcjho4', 0.0) or 0.0)
            )
