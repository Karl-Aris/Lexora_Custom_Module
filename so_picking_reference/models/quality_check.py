from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_out_id = fields.Char(
        string="Delivery Quality Check ID",
        readonly=True
    )

    x_return_id = fields.Char(
        string="Return Quality Check ID",
        readonly=True
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_custom_links()
        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._update_custom_links()
        return res

    def _update_custom_links(self):
        """Update OUT and RETURN quality checks without touching stock.move.line"""
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['stock.picking']

        for rec in self:
            out_names = []
            return_names = []

            picking_outs = StockPicking.search([
                ('sale_id', '=', rec.id),
                ('name', '=like', 'WH/OUT%')
            ])
            if picking_outs:
                quality_checks = QualityCheck.search([
                    ('picking_id', 'in', picking_outs.ids)
                ])
                out_names = quality_checks.mapped('name')

            picking_returns = StockPicking.search([
                ('sale_id', '=', rec.id),
                ('name', '=like', 'WH/IN/RETURN%')
            ])
            if picking_returns:
                quality_checks = QualityCheck.search([
                    ('picking_id', 'in', picking_returns.ids)
                ])
                return_names = quality_checks.mapped('name')

            # assign directly instead of write() → avoids recomputation cascade
            rec.x_out_id = ", ".join(out_names) if out_names else False
            rec.x_return_id = ", ".join(return_names) if return_names else False
