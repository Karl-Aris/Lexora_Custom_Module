from odoo import models, fields, api, _
import base64
import io
import csv
from odoo.exceptions import UserError

class DeductionImportWizard(models.TransientModel):
    _name = "deduction.import.wizard"
    _description = "Deduction Import Wizard"

    file_data = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")
    delimiter = fields.Char(string="Delimiter (CSV)", default=',', help='Delimiter used in CSV files.')
    has_header = fields.Boolean(string='Has header row', default=True)

    def _parse_csv(self, data):
        try:
            text = data.decode('utf-8-sig')
        except Exception:
            text = data.decode('latin-1')
        f = io.StringIO(text)
        reader = csv.reader(f, delimiter=self.delimiter)
        rows = list(reader)
        return rows

    def action_import(self):
        if not self.file_data:
            raise UserError(_('Please upload a file.'))

        data = base64.b64decode(self.file_data)
        rows = self._parse_csv(data)
        if not rows:
            raise UserError(_('File appears to be empty.'))

        # Determine header and data rows
        header = []
        data_rows = []
        if self.has_header:
            header = [h.strip() for h in rows[0]]
            data_rows = rows[1:]
        else:
            # If no header, we will use column indexes; user should upload csv with known column order.
            data_rows = rows

        created = 0
        for r in data_rows:
            # Build a dict if header exists
            row = {}
            if header:
                for i, col in enumerate(header):
                    row[col] = r[i] if i < len(r) else ''
            else:
                # fallback: map common columns by position (best-effort)
                # 0: Deduction #, 1: Customer, 2: PO #, 3: Deduction Date, 4: Deduction Total Amount
                row = {
                    'Deduction #': r[0] if len(r) > 0 else '',
                    'Customer': r[1] if len(r) > 1 else '',
                    'PO #': r[2] if len(r) > 2 else '',
                    'Deduction Date': r[3] if len(r) > 3 else '',
                    'Deduction Total Amount': r[4] if len(r) > 4 else '',
                }

            # resolve partner: try by id then by name
            partner = None
            partner_ref = (row.get('Customer') or '').strip()
            if partner_ref:
                if partner_ref.isdigit():
                    partner = self.env['res.partner'].browse(int(partner_ref))
                else:
                    partner = self.env['res.partner'].search([('name','=',partner_ref)], limit=1)

            vals = {
                'name': (row.get('Deduction #') or '').strip() or None,
                'partner_id': partner.id if partner else None,
                'purchase_order': (row.get('PO #') or '').strip() or None,
                'deduction_date': (row.get('Deduction Date') or '').strip() or None,
                'deduction_total_amount': (row.get('Deduction Total Amount') or '').strip() or 0.0,
                'reason': (row.get('Reason') or '').strip() or None,
                'ticket_status': (row.get('Ticket Status') or '').strip() or 'open',
            }

            if not vals.get('name'):
                # skip empty lines
                continue

            rec = self.env['deduction.vendor'].create(vals)
            created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
