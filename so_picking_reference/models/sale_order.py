from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_pickings_fast(self):
        Picking = self.env['stock.picking']
        for rec in self:
            # ensure we have a purchase_order id
            if not rec.purchase_order or not rec.purchase_order.id:
                _logger.debug('SaleOrder %s: no purchase_order, skipping', rec.id)
                continue

            po_id = rec.purchase_order.id
            vals = {}
            domain_base = [('purchase_order', '=', po_id)]

            # PICK (picking in)
            if not rec.x_picking_in or not rec.x_picking_date:
                picking_in = Picking.search(
                    domain_base + [('name', 'ilike', 'WH/PICK')],
                    order='date_done desc, id desc',
                    limit=1
                )
                _logger.debug('SaleOrder %s: picking_in search returned %s', rec.id, picking_in and picking_in.name)
                if picking_in:
                    if not rec.x_picking_in:
                        vals['x_picking_in'] = picking_in.name
                    if not rec.x_picking_date and picking_in.date_done:
                        vals['x_picking_date'] = picking_in.date_done

            # OUT (delivery out)
            if not rec.x_delivery_out or not rec.x_out_date:
                picking_out = Picking.search(
                    domain_base + [('name', 'ilike', 'WH/OUT')],
                    order='date_done desc, id desc',
                    limit=1
                )
                _logger.debug('SaleOrder %s: picking_out search returned %s', rec.id, picking_out and picking_out.name)
                if picking_out:
                    if not rec.x_delivery_out:
                        vals['x_delivery_out'] = picking_out.name
                    if not rec.x_out_date and picking_out.date_done:
                        vals['x_out_date'] = picking_out.date_done

            # Returns (existing logic)
            if not rec.x_returned or not rec.x_return_date:
                picking_return = Picking.search(
                    domain_base + [('name', 'ilike', 'WH/IN/RETURN')],
                    order='date_done desc, id desc',
                    limit=1
                )
                if picking_return:
                    if not rec.x_returned:
                        vals['x_returned'] = picking_return.name
                    if not rec.x_return_date and picking_return.date_done:
                        vals['x_return_date'] = picking_return.date_done

            if vals:
                _logger.info('SaleOrder %s writing %s', rec.id, vals)
                rec.write(vals)
