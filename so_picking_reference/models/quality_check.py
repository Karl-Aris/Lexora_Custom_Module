from odoo import models, api


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_sale_order_from_quality_check()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_sale_order_from_quality_check()
        return res

    def _update_sale_order_from_quality_check(self):
        """Push data from quality.check into the related sale.order"""
        for rec in self:
            sale_order = rec.picking_id.sale_id
            if sale_order:
                vals = {}

                # Example: push QC name/id into sale.order custom fields
                if not sale_order.x_out_id and rec.picking_id.name.startswith("WH/OUT"):
                    vals['x_out_id'] = rec.id

                if not sale_order.x_return_id and rec.picking_id.name.startswith("WH/IN/RETURN"):
                    vals['x_return_id'] = rec.id

                # You can map more fields here if needed
                # e.g. QC notes, QC date, etc.
                # if rec.notes:
                #     vals['x_qc_notes'] = rec.notes

                if vals:
                    sale_order.write(vals)
