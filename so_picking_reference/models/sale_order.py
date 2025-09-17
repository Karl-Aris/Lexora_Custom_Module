from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # normal SO create (may still touch stock, unavoidable on creation)
        record = super().create(vals)
        # afterwards, only update safe custom fields
        record._update_pickings_fast()
        record._match_invoice_number()
        return record

    def write(self, vals):
        # ⚠️ Only call super().write() if needed
        if vals:
            res = super().write(vals)
        else:
            res = True
        # now run safe updates, bypassing stock logic
        for rec in self:
            rec._update_pickings_fast()
            rec._match_invoice_number()
        return res

    def _update_pickings_fast(self):
        """Update custom picking fields without altering or unlinking stock.move.line"""
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

            # ⚠️ Direct SQL update → avoids ORM triggers/unlink
            if vals:
                self.env.cr.execute("""
                    UPDATE sale_order
                    SET %s
                    WHERE id = %%s
                """ % ", ".join([f"{k} = %s" for k in vals.keys()]),
                    list(vals.values()) + [rec.id]
                )

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
                    # ⚠️ Direct SQL update to avoid ORM triggers
                    self.env.cr.execute("""
                        UPDATE sale_order
                        SET x_invoice_number = %s, x_invoice_date = %s
                        WHERE id = %s
                    """, (invoice.name, invoice.invoice_date, rec.id))
