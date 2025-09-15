from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_out_ids = fields.Char(
        string="OUT Quality Checks",
        readonly=True
    )

    x_return_ids = fields.Char(
        string="Return Pickings",
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
        """Update OUT quality checks and RETURN pickings links"""
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['stock.picking']

        for rec in self:
            # OUT picking & quality checks
            if not rec.x_out_ids:
                picking_out = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/OUT%')
                ])
                if picking_out:
                    quality_checks = QualityCheck.search([
                        ('picking_id', 'in', picking_out.ids)
                    ])
                    if quality_checks:
                        rec.x_out_ids = ", ".join(quality_checks.mapped('name'))

            # RETURN picking & quality checks
            if not rec.x_return_ids:
                picking_return = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/IN/RETURN%')
                ])
                if picking_return:
                    quality_checks = QualityCheck.search([
                        ('picking_id', 'in', picking_return.ids)
                    ])
                    if quality_checks:
                        rec.x_return_ids = ", ".join(quality_checks.mapped('name'))
