from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', string="Related Sale Order")
    x_po_vb_id = fields.Char(string="PO# from Sale Order")

    sale_order_count = fields.Integer(
        compute="_compute_sale_order_count", string="Sale Order Count"
    )

    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = 1 if record.sale_order_id else 0

    def action_view_related_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
