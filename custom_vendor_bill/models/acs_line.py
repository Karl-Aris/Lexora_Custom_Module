from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class ACSPortalLine(models.Model):
    _name = 'x_acs.line'
    _inherit = 'x_acs.line'

    def create_vendor_bill(self):
        bol_to_records = {}
        for rec in self:
            if rec.x_studio_charge_status != 'Approved':
                continue
            if hasattr(rec, 'x_studio_vendor_bill_id') and rec.x_studio_vendor_bill_id:
                continue
            bol_to_records.setdefault(rec.x_studio_bol, []).append(rec)

        product = self.env['product.product'].search([('name', '=', 'Accessorial Charge')], limit=1)
        account = self.env['account.account'].search([('code', '=', '615500')], limit=1)
        if not product or not account:
            raise UserError("⚠️ Product 'Accessorial Charge' or Account 615500 not found")

        today = date.today()

        for bol, recs in bol_to_records.items():
            vendor_id = recs[0].x_studio_carrier_vb.id if recs[0].x_studio_carrier_vb else False
            if not vendor_id:
                continue

            existing_bill = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('partner_id', '=', vendor_id),
                ('ref', '=', bol)
            ], limit=1)

            if existing_bill:
                bill = existing_bill
                if bill.state == 'draft':
                    bill.with_context(validated_analytic=True).action_post()
            else:
                invoice_lines = [(0, 0, {
                    'product_id': product.id,
                    'name': 'Accessorial Charge - BOL %s' % r.x_studio_bol,
                    'quantity': 1,
                    'price_unit': r.x_studio_charged_amount,
                    'account_id': account.id
                }) for r in recs]

                po_ref = recs[0].x_po
                po_ref_with_v = str(po_ref) + '-v' if po_ref else ''

                bill_vals = {
                    'move_type': 'in_invoice',
                    'partner_id': vendor_id,
                    'invoice_origin': recs[0].name or '',
                    'ref': bol,
                    'x_po_vb_id': po_ref_with_v,
                    'invoice_date': today,
                    'invoice_line_ids': invoice_lines
                }

                bill = self.env['account.move'].with_context(validated_analytic=True).create(bill_vals)
                bill.action_post()

            for r in recs:
                if hasattr(r, 'x_studio_vendor_bill_id'):
                    r.write({'x_studio_vendor_bill_id': bill.id})
