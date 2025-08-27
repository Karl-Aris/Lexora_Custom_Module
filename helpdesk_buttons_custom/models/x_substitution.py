from odoo import models, fields, api, _
from odoo.exceptions import UserError

class XSubstitution(models.Model):
    _name = 'x_substitution'  # This must match your model name in Odoo
    _description = 'Substitution Line'

    @api.model
    def perform_substitution(self):
        # This method will be called from Studio button (Call a method)
        for record in self:
            if record.x_result != 'Sub Accepted':
                continue

            if not record.x_ticket_id:
                raise UserError("No Helpdesk Ticket linked to the Substitution record.")

            po_number = record.x_ticket_id.x_po
            if not po_number:
                raise UserError("No PO number found in the linked Helpdesk Ticket.")

            sales_order = self.env['sale.order'].search([('purchase_order', '=', po_number)], limit=1)
            if not sales_order:
                raise UserError("No Sales Order found for PO: %s" % po_number)

            sales_order.write({'x_is_substitution': True})

            old_product = record.x_original_sku
            new_product = record.x_substituted_sku

            if not old_product or not new_product:
                raise UserError("Both old and new SKUs must be set.")

            if not record.x_quantity or not record.x_new_quantity:
                raise UserError("Both old and new quantities must be provided.")

            old_lines = sales_order.order_line.filtered(lambda l: l.product_id.id == old_product.id)

            if not old_lines:
                raise UserError("No matching lines found for product: %s" % old_product.display_name)

            first_line = old_lines[0]
            price_unit = first_line.price_unit
            name = first_line.name

            if sales_order.state == 'draft':
                for line in old_lines:
                    if line.state in ('draft', 'sent'):
                        if line.product_uom_qty == record.x_quantity:
                            line.unlink()
                        elif line.product_uom_qty > record.x_quantity:
                            line.write({'product_uom_qty': line.product_uom_qty - record.x_quantity})
                        else:
                            raise UserError("Substitution quantity is greater than existing line quantity.")
                    else:
                        line.write({'product_uom_qty': 0})
            else:
                for line in old_lines:
                    if line.product_uom_qty >= record.x_quantity:
                        line.write({'product_uom_qty': line.product_uom_qty - record.x_quantity})
                    else:
                        raise UserError("Substitution quantity is greater than existing line quantity.")

            self.env['sale.order.line'].create({
                'order_id': sales_order.id,
                'product_id': new_product.id,
                'product_uom_qty': record.x_new_quantity,
                'price_unit': price_unit,
                'name': name,
            })

            sales_order.message_post(body=(
                "SKU substitution performed:<br/>"
                "<b>%s</b> (Qty: %s) → <b>%s</b> (Qty: %s)" % (
                    old_product.display_name,
                    record.x_quantity,
                    new_product.display_name,
                    record.x_new_quantity
                )
            ))