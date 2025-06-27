from odoo import models, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.depends('x_studio_charged_amount', 'x_studio_monetary_field_782_1iumcjho4')
    def _compute_x_studio_discrepancy(self):
        for rec in self:
            charged = rec.x_studio_charged_amount or 0.0
            processed = rec.x_studio_monetary_field_782_1iumcjho4 or 0.0
            rec.x_studio_discrepancy = charged - processed

    # Apply the compute to existing field using _fields directly
    def __init__(self, pool, cr):
        init_res = super().__init__(pool, cr)
        if 'x_studio_discrepancy' in self._fields:
            self._fields['x_studio_discrepancy'].compute = self._compute_x_studio_discrepancy
            self._fields['x_studio_discrepancy'].store = True
        return init_res