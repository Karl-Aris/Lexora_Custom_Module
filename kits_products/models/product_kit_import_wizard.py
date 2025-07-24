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
            data = io.StringIO(file_data.decode("utf-8"))
            reader = csv.DictReader(data)
        except Exception as e:
            raise ValidationError(_('Invalid file format: %s') % str(e))

        kit_model = self.env['product.kits']
        created = 0

        for row in reader:
            required_fields = ['product_sku', 'name', 'size', 'collection', 'color']
            if not all(row.get(f) for f in required_fields):
                continue  # Skip if essential fields are missing

            kit_model.create({
                'product_sku': row.get('product_sku'),
                'name': row.get('name'),
                'size': row.get('size'),
                'collection': row.get('collection'),
                'color': row.get('color'),
                'cabinet_sku': row.get('cabinet_sku'),
                'counter_top_sku': row.get('counter_top_sku'),
                'faucet_sku': row.get('faucet_sku'),
                'mirror_sku': row.get('mirror_sku'),
            })
            created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Complete'),
                'message': _('%d kits imported successfully.') % created,
                'type': 'success',
                'sticky': False,
            }
        }
