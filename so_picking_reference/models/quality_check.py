from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Clickable links to quality.check records
    x_out_id = fields.Many2one(
        comodel_name='quality.check',
        string="OUT Quality Check",
        readonly=True,
        ondelete='set null',
        index=True,
    )
    x_return_id = fields.Many2one(
        comodel_name='quality.check',
        string="Return Quality Check",
        readonly=True,
        ondelete='set null',
        index=True,
    )

    @api.model
    def create(self, vals):
        records = super().create(vals)
        records._update_quality_checks_fast()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._update_quality_checks_fast()
        return res

    def _update_quality_checks_fast(self):
        """Link OUT/RETURN quality checks to sale orders."""
        QualityCheck = self.env['quality.check']

        sale_orders = self.filtered(lambda so: so.order_line and (not so.x_out_id or not so.x_return_id))
        if not sale_orders:
            return

        sale_order_names = sale_orders.mapped("name")

        qc_records = QualityCheck.search([
            ('picking_id.origin', 'in', sale_order_names),
            '|',
            ('picking_id.name', 'ilike', 'WH/OUT/'),
            ('picking_id.name', 'ilike', 'WH/IN/RETURN/')
        ])

        # Group by sale order origin
        qc_by_origin = {}
        for qc in qc_records:
            qc_by_origin.setdefault(qc.picking_id.origin, []).append(qc)

        for so in sale_orders:
            updates = {}
            qc_list = qc_by_origin.get(so.name, [])

            if not so.x_out_id:
                qc_out = next((q for q in qc_list if q.picking_id.name.startswith('WH/OUT')), False)
                if qc_out:
                    updates['x_out_id'] = qc_out.id

            if not so.x_return_id:
                qc_return = next((q for q in qc_list if q.picking_id.name.startswith('WH/IN/RETURN')), False)
                if qc_return:
                    updates['x_return_id'] = qc_return.id

            if updates:
                # Prevent recursive write effects (mail, followers, etc.)
                super(SaleOrder, so.with_context(mail_notrack=True, mail_auto_subscribe=False)).write(updates)
