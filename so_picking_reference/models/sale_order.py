from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_picking_in = fields.Char(string="Picking IN Ref", readonly=True)
    x_delivery_out = fields.Char(string="Delivery OUT Ref", readonly=True)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_picking_refs()
        return record

    def write(self, vals):
        result = super().write(vals)
        self._update_picking_refs()
        return result

    def _update_picking_refs(self):
        for order in self:
            if not order.purchase_order:
                continue

            domain = [
                ('purchase_order', '=', order.purchase_order),
                ('name', 'ilike', 'WH/%')
            ]
            pickings = self.env['stock.picking'].search(domain)

            picking_in = next((p.name for p in pickings if 'WH/PICK' in p.name), False)
            picking_out = next((p.name for p in pickings if 'WH/OUT' in p.name), False)

            updates = {}
            if picking_in and not order.x_picking_in:
                updates['x_picking_in'] = picking_in
            if picking_out and not order.x_delivery_out:
                updates['x_delivery_out'] = picking_out

            if updates:
                order.write(updates)
