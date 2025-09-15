from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_out_id = fields.Char(
        string="OUT Quality Check",
        readonly=True
    )

    x_return_id = fields.Char(
        string="Return Picking",
        readonly=True
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_custom_links()
        return record

    def write(self, vals):
        res = super().write(vals)
        # call after super, but avoid recursion
        self._update_custom_links()
        return res

    def _update_custom_links(self):
        """Update OUT quality check and RETURN picking link safely"""
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['stock.picking']

        for rec in self:
            updates = {}

            # OUT picking & quality check
            if not rec.x_out_id :
                picking_out = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/OUT%')
                ], limit=1)

                if picking_out:
                    quality_check = QualityCheck.search(
                        [('picking_id', '=', picking_out.id)],
                        limit=1
                    )
                    if quality_check:
                        updates['x_out_id '] = quality_check.name

            # RETURN picking
            if not rec.x_return_id:
                picking_return = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/IN/RETURN%')
                ], limit=1)

                if picking_return:
                    quality_check_return = QualityCheck.search(
                        [('picking_id', '=', picking_return.id)],
                        limit=1
                    )
                    if quality_check_return:
                        updates['x_return_id'] = quality_check_return.name

            if updates:
                rec.update(updates)  # ✅ safe, does not trigger mail followers or deletes

