from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_pickings_fast()
        record._safe_tag_invoice_number()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_pickings_fast()
        self._safe_tag_invoice_number()
        return res

    def _update_pickings_fast(self):
        Picking = self.env['stock.picking']
        for rec in self:
            if not rec.purchase_order:
                continue

            vals = {}
            domain_base = [('purchase_order', '=', rec.purchase_order)]

            if not rec.x_picking_in:
                picking_in = Picking.search(
                    domain_base + [('name', '=like', 'WH/PICK%')],
                    limit=1
                )
                if picking_in:
                    vals['x_picking_in'] = picking_in.name

            if not rec.x_delivery_out:
                picking_out = Picking.search(
                    domain_base + [('name', '=like', 'WH/OUT%')],
                    limit=1
                )
                if picking_out:
                    vals['x_delivery_out'] = picking_out.name

            if vals:
                rec.write(vals)

    def _safe_tag_invoice_number(self):
        Invoice = self.env['account.move']
        for record in self:
            # Only tag if purchase_order exists and x_invoice_number is not already set
            if record.purchase_order and not record.x_invoice_number:
                matched_invoice = Invoice.search([
                    ('x_po_so_id', '=', record.purchase_order),
                ], limit=1)
                if matched_invoice:
                    try:
                        record.x_invoice_number = matched_invoice.name
                    except Exception as e:
                        # Log or handle the exception gracefully
                        _logger = self.env['ir.logging']
                        _logger.create({
                            'name': 'Invoice Tagging Error',
                            'type': 'server',
                            'level': 'error',
                            'message': str(e),
                            'path': 'sale.order',
                            'func': '_safe_tag_invoice_number',
                            'line': '0',
                        })
