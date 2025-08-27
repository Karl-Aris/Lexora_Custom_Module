from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.fields import Command


class XSubstitution(models.Model):
    _inherit = 'x_substitution'  # Adjust if needed

    def perform_substitution(self):
        for record in self:
            if not record.x_ticket_id:
                raise UserError("No Helpdesk Ticket linked to the Substitution record.")

            po_number = record.x_ticket_id.x_po
            if not po_number:
                raise UserError("No PO number found in the linked Helpdesk Ticket.")

            sales_order = self.env['sale.order'].search([('purchase_order', '=', po_number)], limit=1)
            if not sales_order:
                raise UserError("No Sales Order found for PO: %s" % po_number)

            substitution_lines = []
            for line in sales_order.order_line:
                substitution_lines.append(Command.create({
                    'x_original_sku': line.product_id.id,
                    'x_quantity': line.product_uom_qty,
                    'x_substituted_sku': False,
                    'x_new_quantity': 0.0,
                    'x_note': '',
                    'x_result': '',
                }))

            record.write({
                'x_substitution_lines': substitution_lines  # Replace with your actual One2many field
            })
