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
        """Safely update OUT quality checks and RETURN pickings links
        without deleting or altering stock.move/stock.picking records
        """
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['stock.picking']

        for rec in self:
            # OUT picking & quality checks (only read, never delete)
            if not rec.x_out_id:
                picking_out = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/OUT%')
                ], limit=1)
                if picking_out:
                    quality_checks = QualityCheck.search([
                        ('picking_id', '=', picking_out.id)
                    ])
                    if quality_checks:
                        rec.sudo().write({
                            'x_out_id': ", ".join(quality_checks.mapped('name'))
                        })

            # RETURN picking & quality checks (only read, never delete)
            if not rec.x_return_id:
                picking_return = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/IN/RETURN%')
                ], limit=1)
                if picking_return:
                    quality_checks = QualityCheck.search([
                        ('picking_id', '=', picking_return.id)
                    ])
                    if quality_checks:
                        rec.sudo().write({
                            'x_return_id': ", ".join(quality_checks.mapped('name'))
                        })
