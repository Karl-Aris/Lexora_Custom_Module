from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_pickings_fast()
        record._match_invoice_number()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_pickings_fast()
        self._match_invoice_number()
        return res

    def _update_pickings_fast(self):
        Picking = self.env['stock.picking']
        for rec in self:
            vals = {}

            # Outgoing (delivery)
            if not rec.x_out_date:
                picking_out = Picking.search(
                    [('sale_id', '=', rec.id), ('picking_type_id.code', '=', 'outgoing')],
                    order='date_done desc, id desc',
                    limit=1
                )
                if picking_out and picking_out.date_done:
                    vals['x_out_date'] = picking_out.date_done
                    vals['x_delivery_out'] = picking_out.name

            # Picking (internal transfer to staging)
            if not rec.x_picking_date:
                picking_in = Picking.search(
                    [('sale_id', '=', rec.id), ('picking_type_id.code', '=', 'internal')],
                    order='date_done desc, id desc',
                    limit=1
                )
                if picking_in and picking_in.date_done:
                    vals['x_picking_date'] = picking_in.date_done
                    vals['x_picking_in'] = picking_in.name

            if vals:
                rec.write(vals)


    def _match_invoice_number(self):
        Move = self.env['account.move']
        for rec in self:
            if rec.purchase_order and (not rec.x_invoice_number or not rec.x_invoice_date):
                invoice = Move.search([
                    ('x_po_so_id', '=', rec.purchase_order),
                    ('state', '=', 'posted'),
                    ('name', '!=', '/'),
                ], limit=1)
                if invoice:
                    vals = {}
                    if not rec.x_invoice_number:
                        vals['x_invoice_number'] = invoice.name
                    if not rec.x_invoice_date and invoice.invoice_date:
                        vals['x_invoice_date'] = invoice.invoice_date
                    if vals:
                        rec.write(vals)
