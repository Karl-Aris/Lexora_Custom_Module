from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Using existing Studio-created fields:
    # No need to redeclare them here unless you want to change something

    @api.model
    def _get_related_pickings(self, po_number):
        return self.env['stock.picking'].search([
            ('purchase_order', '=', po_number),
            ('name', 'ilike', 'WH/%'),
        ])

    def _get_related_invoice(self, po_number):
        return self.env['account.move'].search([
            ('x_po_so_id', '=', po_number),
        ], limit=1)

    def write(self, vals):
        res = super().write(vals)

        for record in self:
            # Set Picking IN/OUT references
            if record.purchase_order and (not record.x_picking_in or not record.x_delivery_out):
                pickings = self._get_related_pickings(record.purchase_order)
                updates = {}

                if not record.x_picking_in:
                    picking_in = next((p for p in pickings if 'WH/PICK' in p.name), None)
                    if picking_in:
                        updates['x_picking_in'] = picking_in.name

                if not record.x_delivery_out:
                    picking_out = next((p for p in pickings if 'WH/OUT' in p.name), None)
                    if picking_out:
                        updates['x_delivery_out'] = picking_out.name

                if updates:
                    record.super().write(updates)

            # Set Invoice # reference
            if record.purchase_order and not record.x_invoice_number:
                invoice = self._get_related_invoice(record.purchase_order)
                if invoice:
                    record.super().write({
                        'x_invoice_number': invoice.name
                    })

        return res
