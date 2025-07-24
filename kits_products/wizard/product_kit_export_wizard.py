# kits_products/wizards/product_kit_export_wizard.py

from odoo import models, fields
import io
import base64
import csv

class ProductKitExportWizard(models.TransientModel):
    _name = 'product.kit.export.wizard'
    _description = 'Export Product Kits Wizard'

    file = fields.Binary('Exported File', readonly=True)
    filename = fields.Char('Filename', default='kits_export.csv')

    def export_kits(self):
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['SKU', 'Name', 'Size', 'Collection', 'Color'])

        # Fetch kit data (adjust model/fields as needed)
        kits = self.env['product.kits'].search([])
        for kit in kits:
            writer.writerow([
                kit.product_sku or '',
                kit.name or '',
                kit.size or '',
                kit.collection or '',
                kit.color or '',
            ])

        output.seek(0)
        self.file = base64.b64encode(output.getvalue().encode('utf-8'))
        output.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.kit.export.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }
