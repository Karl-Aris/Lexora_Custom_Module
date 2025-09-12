from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_quality_checks_fast(self):
        """Push quality.check IDs into sale.order fields"""
        QualityCheck = self.env['quality.check']
        for rec in self:
            if not rec.order_line:  # make sure it's a valid SO
                continue

            vals = {}
            domain_base = [('picking_id.sale_id', '=', rec.id)]

            # OUT quality check → x_out_id
            if not rec.x_out_id:
                qc_out = QualityCheck.search(
                    domain_base + [('picking_id.name', '=like', 'WH/OUT%')],
                    limit=1
                )
                if qc_out:
                    vals['x_out_id'] = qc_out.id

            # RETURN quality check → x_return_id
            if not rec.x_return_id:
                qc_return = QualityCheck.search(
                    domain_base + [('picking_id.name', '=like', 'WH/IN/RETURN%')],
                    limit=1
                )
                if qc_return:
                    vals['x_return_id'] = qc_return.id

            if vals:
                rec.write(vals)
