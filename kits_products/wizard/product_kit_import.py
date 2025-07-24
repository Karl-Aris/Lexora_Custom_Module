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

        file_data = base64.b64decode(self.file)
        data = io.StringIO(file_data.decode("utf-8-sig"))  # handles BOM
        reader = csv.DictReader(data)

        for row in reader:
            try:
                self.env['product.kits'].create({
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
            except Exception as e:
                raise ValidationError(_('Error creating product kit for row: %s\n\n%s') % (row, str(e)))
