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
        self._update_custom_links()
        return res

    def _update_custom_links(self):
        """Optimized: batch fetch pickings and quality checks"""
        StockPicking = self.env['stock.picking']
        QualityCheck = self.env['quality.check']

        sale_ids = self.ids
        if not sale_ids:
            return

        # Fetch all pickings in one go
        pickings = StockPicking.search([('sale_id', 'in', sale_ids)])
        picking_by_sale = {}
        for picking in pickings:
            picking_by_sale.setdefault(picking.sale_id.id, []).append(picking)

        # Fetch all quality checks in one go
        quality_checks = QualityCheck.search([('picking_id', 'in', pickings.ids)])
        qc_by_picking = {}
        for qc in quality_checks:
            qc_by_picking.setdefault(qc.picking_id.id, []).append(qc.name)

        # Build vals per sale order
        for rec in self:
            vals = {}
            pcks = picking_by_sale.get(rec.id, [])

            # OUT pickings
            out_picks = [p for p in pcks if p.name.startswith('WH/OUT')]
            if out_picks and not rec.x_out_id:
                qc_names = []
                for p in out_picks:
                    qc_names.extend(qc_by_picking.get(p.id, []))
                if qc_names:
                    vals['x_out_id'] = ", ".join(qc_names)

            # RETURN pickings
            return_picks = [p for p in pcks if p.name.startswith('WH/IN/RETURN')]
            if return_picks and not rec.x_return_id:
                qc_names = []
                for p in return_picks:
                    qc_names.extend(qc_by_picking.get(p.id, []))
                if qc_names:
                    vals['x_return_id'] = ", ".join(qc_names)

            if vals:
                # Safe write (no recursion)
                super(SaleOrder, rec).write(vals)
