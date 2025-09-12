from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_quality_checks_fast()  # auto-update quality checks
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_quality_checks_fast()  # auto-update quality checks
        return res

    def _update_quality_checks_fast(self):
        """Push quality.check IDs into sale.order fields"""
        QualityCheck = self.env['quality.check']
        for rec in self:
            vals = {}

            # OUT quality check → x_out_id
            if not rec.x_out_id:
                qc_out = QualityCheck.search([
                    ('picking_id.origin', '=like', rec.name + '%'),  # link via sale order name
                    ('picking_id.name', '=like', 'WH/OUT%')
                ], limit=1)
                if qc_out:
                    vals['x_out_id'] = qc_out.id

            # RETURN quality check → x_return_id
            if not rec.x_return_id:
                qc_return = QualityCheck.search([
                    ('picking_id.origin', '=like', rec.name + '%'),
                    ('picking_id.name', '=like', 'WH/IN/RETURN%')
                ], limit=1)
                if qc_return:
                    vals['x_return_id'] = qc_return.id

            if vals:
                rec.write(vals)
