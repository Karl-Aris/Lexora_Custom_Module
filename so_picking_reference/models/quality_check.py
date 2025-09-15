from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_out_id = fields.Char(
        string="OUT Quality Check",
        compute="_compute_custom_links",
        store=True,
        readonly=True
    )

    x_return_id = fields.Char(
        string="Return Picking",
        compute="_compute_custom_links",
        store=True,
        readonly=True
    )

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_custom_links(self):
        """Compute OUT quality check and RETURN picking safely"""
        QualityCheck = self.env['quality.check']
        for rec in self:
            out_val, return_val = False, False

            # OUT picking & quality check
            picking_out = rec.picking_ids.filtered(
                lambda p: p.name.startswith('WH/OUT')
            )[:1]
            if picking_out:
                quality_check = QualityCheck.search(
                    [('picking_id', '=', picking_out.id)],
                    limit=1
                )
                if quality_check:
                    out_val = quality_check.name

            # RETURN picking
            picking_return = rec.picking_ids.filtered(
                lambda p: p.name.startswith('WH/IN/RETURN')
            )[:1]
            if picking_return:
                quality_check_return = QualityCheck.search(
                    [('picking_id', '=', picking_return.id)],
                    limit=1
                )
                if quality_check_return:
                    return_val = quality_check_return.name

            rec.x_out_id = out_val
            rec.x_return_id = return_val
