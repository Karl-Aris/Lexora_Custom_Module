from odoo import models, fields, api

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    x_location = fields.Char(
        string="Location",
        compute="_compute_x_location",
        store=True
    )
    x_condition = fields.Char(
        string="Condition",
        compute="_compute_x_condition",
        store=True
    )

    @api.depends('picking_id.name')
    def _compute_x_location(self):
        for rec in self:
            if rec.picking_id and "WH/IN/RETURN" in rec.picking_id.name:
                rec.x_location = rec.picking_id.name
            else:
                rec.x_location = False

    @api.depends('quality_state')
    def _compute_x_condition(self):
        for rec in self:
            if rec.quality_state == 'fail':
                rec.x_condition = "Damaged"
            elif rec.quality_state == 'pass':
                rec.x_condition = "Good"
            else:
                rec.x_condition = ""
