from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # New fields
    x_out_id = fields.Many2one(
        'quality.check',
        string="OUT Quality Check",
        readonly=True
    )
    x_return_id = fields.Many2one(
           'quality.check',
        string="Return Picking",
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
        """Update OUT quality check and RETURN picking link"""
        Picking = self.env['quality.check']
        QualityCheck = self.env['quality.check']

        for rec in self:
            # OUT picking & quality check
            if not rec.x_out_id:
                picking_out = QualityCheck.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/OUT%')
                ], limit=1)

                
                if picking_out:
                    rec.x_out_id = picking_out.id

            # RETURN picking
            if not rec.x_return_id:
                picking_return = Picking.search([
                    ('sale_id', '=', rec.id),
                    ('name', '=like', 'WH/IN/RETURN%')
                ], limit=1)

                if picking_return:
                    rec.x_return_id = picking_return.id
