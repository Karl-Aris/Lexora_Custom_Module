from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_serial_number = fields.Char(string='Serial / Batch No.')
    x_quality_checked = fields.Boolean(string='Quality Checked', default=False)
    x_location_verified = fields.Boolean(string='Location Verified', compute='_compute_location_verified', store=True)
    x_note = fields.Text(string='Internal Note')

    @api.depends('location_id')
    def _compute_location_verified(self):
        for rec in self:
            rec.x_location_verified = bool(rec.location_id)

    @api.constrains('x_serial_number')
    def _check_serial_unique_on_location(self):
        for rec in self:
            if not rec.x_serial_number:
                continue
            domain = [
                ('id', '!=', rec.id),
                ('product_id', '=', rec.product_id.id),
                ('x_serial_number', '=', rec.x_serial_number),
                ('location_id', '=', rec.location_id.id),
            ]
            exists = self.search(domain, limit=1)
            if exists:
                raise ValidationError(_("Serial/Batch '%s' already exists for this product in the same location.") % rec.x_serial_number)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        try:
            if rec.product_id and rec.product_id.type == 'consu':
                rec.x_quality_checked = True
        except Exception:
            pass
        return rec

    def write(self, vals):
        res = super().write(vals)
        if 'x_serial_number' in vals:
            for rec in self:
                rec.x_quality_checked = False
        return res
