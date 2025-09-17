from odoo import models, fields, api, _

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
        # call update after create (normal external context)
        record._update_custom_links()
        return record

    def write(self, vals):
        # If context asks to skip the recursing update, just perform normal write
        if self.env.context.get('skip_custom_links'):
            return super().write(vals)

        res = super().write(vals)
        # Update links for each record (will use direct SQL to avoid ORM cascades)
        for rec in self:
            rec._update_custom_links()
        return res

    def _write_direct(self, vals):
        """Write directly in DB to avoid triggering automations / recomputations.
        vals is a dict of column_name -> value for this model (ORM field names).
        Warning: this avoids ORM hooks — only update simple scalar fields.
        """
        if not vals:
            return
        table = self._table  # e.g. 'sale_order'
        # build SQL sets
        for rec in self:
            columns = []
            params = []
            for key, value in vals.items():
                # Only allow simple scalar types (char, boolean, numeric, null)
                columns.append(f"{key} = %s")
                params.append(value)
            params.append(rec.id)
            sql = f"UPDATE {table} SET {', '.join(columns)} WHERE id = %s"
            self.env.cr.execute(sql, params)
        # Invalidate cache for updated fields so subsequent reads are correct
        fields_to_invalidate = list(vals.keys())
        self.invalidate_cache(fnames=fields_to_invalidate, records=self)

    def _update_custom_links(self):
        """Safely compute OUT and RETURN quality check *names* and persist them
        without triggering ORM write cascades that may regenerate/unlink stock moves.
        """
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

            vals = {
                'x_out_id': ", ".join(out_names) if out_names else False,
                'x_return_id': ", ".join(return_names) if return_names else False,
            }

            # Use direct DB write to avoid triggering write hooks / automations
            # that cause recursion and stock move recalculations.
            rec.with_context(skip_custom_links=True)._write_direct(vals)
