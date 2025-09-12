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
            picking = rec.picking_id
            if not picking or not picking.sale_id:
                continue  # skip if no related sale order

            sale_order = picking.sale_id
            update_vals = {}

            # OUT picking → link to sale.order.x_out_id
            if not sale_order.x_out_id and picking.name and picking.name.startswith("WH/OUT"):
                update_vals['x_out_id'] = rec.id

            # RETURN picking → link to sale.order.x_return_id
            if not sale_order.x_return_id and picking.name and picking.name.startswith("WH/IN/RETURN"):
                update_vals['x_return_id'] = rec.id

            if update_vals:
                sale_order.write(update_vals)
