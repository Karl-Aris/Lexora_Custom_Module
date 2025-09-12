from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Many2one fields are clickable in the form view and will open the linked record
    x_out_id = fields.Many2one(
        comodel_name='quality.check',
        string="OUT Quality Check",
        readonly=True,
        ondelete="set null"
    )

    x_return_id = fields.Many2one(
        comodel_name='quality.check',
        string="Return Quality Check",
        readonly=True,
        ondelete="set null"
    )

    @api.model
    def create(self, vals):
        """Batch-safe create method"""
        records = super().create(vals)
        records._update_quality_checks_fast()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._update_quality_checks_fast()
        return res

    def _update_quality_checks_fast(self):
        """Push quality.check IDs into sale.order fields"""
        QualityCheck = self.env['quality.check']

        sale_orders = self.filtered(lambda so: so.order_line)
        if not sale_orders:
            return

        sale_order_names = sale_orders.mapped("name")

        qc_records = QualityCheck.search([
            ('picking_id.origin', 'in', sale_order_names),
            '|',
            ('picking_id.name', '=like', 'WH/OUT%'),
            ('picking_id.name', '=like', 'WH/IN/RETURN%')
        ])

        for so in sale_orders:
            vals = {}

            # OUT QC → x_out_id
            if not so.x_out_id:
                qc_out = qc_records.filtered(
                    lambda q: q.picking_id.origin == so.name
                    and q.picking_id.name.startswith('WH/OUT')
                )
                if qc_out:
                    vals['x_out_id'] = qc_out[0].id

            # RETURN QC → x_return_id
            if not so.x_return_id:
                qc_return = qc_records.filtered(
                    lambda q: q.picking_id.origin == so.name
                    and q.picking_id.name.startswith('WH/IN/RETURN')
                )
                if qc_return:
                    vals['x_return_id'] = qc_return[0].id

            if vals:
                # avoid mail.thread followers duplication
                so.with_context(mail_notrack=True, mail_auto_subscribe=False).write(vals)
