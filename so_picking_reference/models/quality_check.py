from odoo import models, fields, api, _

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
        # Keep normal behaviour for external creates
        record._update_custom_links()
        return record

    def write(self, vals):
        # Normal write, but avoid recursion when context requests it
        if self.env.context.get("skip_custom_links"):
            return super().write(vals)

        res = super().write(vals)
        # Update links for each record (guarded)
        for rec in self:
            rec._update_custom_links()
        return res

    def _update_custom_links(self):
        """Safely update OUT and RETURN quality check names without deleting stock moves."""
        # Prevent recursion if called from our own internal write
        if self.env.context.get("skip_custom_links"):
            return

        QualityCheck = self.env["quality.check"]
        StockPicking = self.env["stock.picking"]

        for rec in self:
            out_names = []
            return_names = []

            # OUT pickings -> quality checks
            picking_outs = StockPicking.search([
                ("sale_id", "=", rec.id),
                ("name", "=like", "WH/OUT%")
            ])
            if picking_outs:
                qcs = QualityCheck.search([("picking_id", "in", picking_outs.ids)])
                out_names = qcs.mapped("name")

            # RETURN pickings -> quality checks
            picking_returns = StockPicking.search([
                ("sale_id", "=", rec.id),
                ("name", "=like", "WH/IN/RETURN%")
            ])
            if picking_returns:
                qcs = QualityCheck.search([("picking_id", "in", picking_returns.ids)])
                return_names = qcs.mapped("name")

            vals = {
                "x_out_id": ", ".join(out_names) if out_names else False,
                "x_return_id": ", ".join(return_names) if return_names else False,
            }

            # Use the skip_context so our write doesn't call _update_custom_links again
            rec.with_context(skip_custom_links=True)._write_direct(vals)

    def _write_direct(self, vals):
        """Perform a direct, guarded write and invalidate cache correctly.

        This uses the normal ORM write but passes the context that avoids
        recursively calling _update_custom_links. Afterwards we invalidate the cache
        for the updated fields using the correct call signature.
        """
        if not vals:
            return

        # Use ORM write but with skip_custom_links already set by caller
        super(SaleOrder, self).write(vals)

        # Invalidate cache properly — pass field list as positional argument.
        fields_to_invalidate = list(vals.keys())
        if fields_to_invalidate:
            # NOTE: pass field list positionally (no fnames= keyword)
            self.env.cache.invalidate(self, fields_to_invalidate)
