from odoo import models, fields, _
from odoo.exceptions import ValidationError
import base64
import io
import csv

class ProductKitImportWizard(models.TransientModel):
    _name = 'product.kit.import.wizard'
    _description = 'Import Product Kits Wizard'

    file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def import_product_kits(self):
        if not self.file:
            raise ValidationError(_('Please upload a CSV file.'))

        try:
            file_data = base64.b64decode(self.file)
            data = io.StringIO(file_data.decode("utf-8-sig"))  # handles BOM
            reader = csv.DictReader(data)
        except Exception as e:
            raise ValidationError(_('Could not decode CSV: %s') % str(e))

        Kit = self.env['product.kits']
        created, updated = 0, 0

        for row in reader:
            try:
                record = None
                raw_id = row.get('id')
                sku = (row.get('product_sku') or '').strip()

                if raw_id and raw_id.isdigit():
                    record = Kit.browse(int(raw_id))
                    if not record.exists():
                        record = None

                if not record and sku:
                    record = Kit.search([('product_sku', '=', sku)], limit=1)

                vals = {
                    'product_sku': sku,
                    'name': row.get('name'),
                    'size': row.get('size'),
                    'collection': row.get('collection'),
                    'color': row.get('color'),
                    'cabinet_sku': row.get('cabinet_sku'),
                    'counter_top_sku': row.get('counter_top_sku'),
                    'faucet_sku': row.get('faucet_sku'),
                    'mirror_sku': row.get('mirror_sku'),
                }

                if record:
                    record.write(vals)
                    updated += 1
                else:
                    Kit.create(vals)
                    created += 1

            except Exception as e:
                raise ValidationError(_('Error on row:\n%s\n\n%s') % (row, str(e)))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Finished'),
                'message': _('✅ Kits Imported\nCreated: %s\nUpdated: %s') % (created, updated),
                'type': 'success',
                'sticky': False,
            }
        }
