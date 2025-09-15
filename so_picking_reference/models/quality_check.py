from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Use Char fields instead of Many2one
    x_out_quality_ref = fields.Char(
        string="OUT Quality Check Ref",
        readonly=True
    )
    x_return_ref = fields.Char(
        string="Return Picking Ref",
        readonly=True
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_custom_links()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_custom_links()
        return res

    def _update_custom_links(self):
        """Update OUT quality check and RETURN picking references"""
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['quality.check']

        for rec in self:
            # OUT picking & quality check
            if not rec.x_out_quality_ref:
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
                        rec.x_out_quality_ref = quality_check.name  # ✅ now valid, storing string

            # RETURN picking
            if not rec.x_return_ref:
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
                        rec.x_return_ref = quality_check_return.name  # ✅ now valid
