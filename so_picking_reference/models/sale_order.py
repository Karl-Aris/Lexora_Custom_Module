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
        """Update custom picking fields without altering stock.move.line"""
        Picking = self.env['stock.picking']
        for rec in self:
            if not rec.purchase_order:
                continue

            vals = {}
            domain_base = [('purchase_order', '=', rec.purchase_order)]

            # IN picking
            if not rec.x_picking_in:
                picking_in = Picking.search(
                    domain_base + [('name', '=like', 'WH/PICK%')],
                    limit=1
                )
                if picking_in:
                    vals['x_picking_in'] = picking_in.name or ''
                    vals['x_picking_date'] = picking_in.date_done or False
                    
            # OUT picking
            if not rec.x_delivery_out:
                picking_out = Picking.search(
                    domain_base + [('name', '=like', 'WH/OUT%')],
                    limit=1
                )
                if picking_out:
                    vals['x_delivery_out'] = picking_out.name or ''
                    vals['x_out_date'] = picking_out.date_done or False

            # RETURN picking
            if not rec.x_returned or not rec.x_return_date:
                picking_return = Picking.search(
                    domain_base + [('name', '=like', 'WH/IN/RETURN%')],
                    limit=1
                )
                if picking_return:
                    if not rec.x_returned:
                        vals['x_returned'] = picking_return.name or ''
                    if not rec.x_return_date and picking_return.date_done:
                        vals['x_return_date'] = picking_return.date_done

            # Only update custom Char/Date fields (safe, no unlink risk)
            if vals:
                rec.sudo().write(vals)

    def _match_invoice_number(self):
        """Match posted invoice number without touching stock.move.line"""
        Move = self.env['account.move']
        for rec in self:
            if rec.purchase_order and not rec.x_invoice_number:
                invoice = Move.search([
                    ('x_po_so_id', '=', rec.purchase_order),
                    ('state', '=', 'posted'),
                    ('name', '!=', '/'),
                ], limit=1)
                if invoice:
                    rec.sudo().write({
                        'x_invoice_number': invoice.name,
                        'x_invoice_date': invoice.invoice_date,
                    })
