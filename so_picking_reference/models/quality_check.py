from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

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
        # prevent recursion loops
        if not self.env.context.get("skip_custom_links"):
            for rec in self:
                rec._update_custom_links()
        return res

    def _update_custom_links(self):
        """Safely update OUT and RETURN quality checks without deleting stock.move/lines."""
        if self.env.context.get("skip_custom_links"):
            return

        QualityCheck = self.env["quality.check"]
        StockPicking = self.env["stock.picking"]

        for rec in self:
            # OUT picking & quality checks
            if not rec.x_out_id:
                picking_out = StockPicking.search([
                    ("sale_id", "=", rec.id),
                    ("name", "=like", "WH/OUT%")
                ], limit=1)
                if picking_out:
                    quality_checks = QualityCheck.search([
                        ("picking_id", "=", picking_out.id)
                    ])
                    if quality_checks:
                        rec.with_context(skip_custom_links=True)._write_direct({
                            "x_out_id": ", ".join(quality_checks.mapped("name"))
                        })

            # RETURN picking & quality checks
            if not rec.x_return_id:
                picking_return = StockPicking.search([
                    ("sale_id", "=", rec.id),
                    ("name", "=like", "WH/IN/RETURN%")
                ], limit=1)
                if picking_return:
                    quality_checks = QualityCheck.search([
                        ("picking_id", "=", picking_return.id)
                    ])
                    if quality_checks:
                        rec.with_context(skip_custom_links=True)._write_direct({
                            "x_return_id": ", ".join(quality_checks.mapped("name"))
                        })

    def _write_direct(self, vals):
        """Bypass custom links recursion and properly invalidate cache."""
        super(SaleOrder, self).write(vals)

        fields_to_invalidate = list(vals.keys())
        if fields_to_invalidate:
            # Proper Odoo cache invalidation
            self.env.cache.invalidate(self, fnames=fields_to_invalidate)
