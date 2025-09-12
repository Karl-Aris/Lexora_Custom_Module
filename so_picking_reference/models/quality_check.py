from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals_list):
        """Batch-safe create method"""
        records = super().create(vals_list)
        records._update_quality_checks_fast()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._update_quality_checks_fast()
        return res

    def _update_quality_checks_fast(self):
        """Push quality.check IDs into sale.order fields"""
        QualityCheck = self.env['quality.check']

        # Collect all sale order names to search QC records in batch
        sale_order_map = {so.id: so for so in self if so.order_line}

        if not sale_order_map:
            return

        # Search all relevant quality.check records in one query
        qc_records = QualityCheck.search([
            ('picking_id.origin', 'in', list(sale_order_map.values())),
            '|',
            ('picking_id.name', '=like', 'WH/OUT%'),
            ('picking_id.name', '=like', 'WH/IN/RETURN%')
        ])

        for so in sale_order_map.values():
            vals = {}

            # OUT QC
            qc_out = qc_records.filtered(lambda q: q.picking_id.origin == so.name and q.picking_id.name.startswith('WH/OUT'))
            if qc_out and not so.x_out_id:
                vals['x_out_id'] = qc_out[0].id

            # RETURN QC
            qc_return = qc_records.filtered(lambda q: q.picking_id.origin == so.name and q.picking_id.name.startswith('WH/IN/RETURN'))
            if qc_return and not so.x_return_id:
                vals['x_return_id'] = qc_return[0].id

            if vals:
                so.write(vals)

