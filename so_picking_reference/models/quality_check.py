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
        # First create the record
        record = super().create(vals)
        # Then update only custom fields
        record._update_custom_links()
        return record

    def write(self, vals):
        # ⚠️ Run custom link update BEFORE super().write()
        self._update_custom_links()
        return super().write(vals)

    def _update_custom_links(self):
        """Update OUT and RETURN quality check info
        without ever calling or triggering unlink()
        """
        QualityCheck = self.env['quality.check']
        StockPicking = self.env['stock.picking']

        for rec in self:
            updates = {}

            # OUT picking & quality checks
            if not rec.x_out_id:
                picking_out = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/OUT%')
                ], limit=1)
                if picking_out:
                    qc = QualityCheck.search([('picking_id', '=', picking_out.id)])
                    if qc:
                        updates['x_out_id'] = ", ".join(qc.mapped('name'))

            # RETURN picking & quality checks
            if not rec.x_return_id:
                picking_return = StockPicking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/IN/RETURN%')
                ], limit=1)
                if picking_return:
                    qc = QualityCheck.search([('picking_id', '=', picking_return.id)])
                    if qc:
                        updates['x_return_id'] = ", ".join(qc.mapped('name'))

            # ⚠️ Write only to primitive fields, bypassing stock logic
            if updates:
                rec.with_context(bypass_unlink=True).sudo().write(updates)
