from odoo import models, api
from odoo.exceptions import UserError

class XSubstitution(models.Model):
    _inherit = 'x_substitution'

    @api.multi
    def perform_substitution(self):
        for record in self:
            if record.x_result != 'Sub Accepted':
                continue
            if not record.x_ticket_id:
                raise UserError("No Helpdesk Ticket linked to the substitution record.")
            po_number = record.x_ticket_id.x_po
            if not po_number:
                raise UserError("No PO number found in linked Helpdesk Ticket.")

            sale_order = self.env['sale.order'].search([('purchase_order', '=', po_number)], limit=1)
            if not sale_order:
                raise UserError(f"No Sales Order found for PO: {po_number}")

            # ... your substitution logic to edit sale_order lines here ...
            # (reuse the code you have for modifying lines and adding new line)

            sale_order.message_post(body=f"Substitution done based on PO: {po_number}")
