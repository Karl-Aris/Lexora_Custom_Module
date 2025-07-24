from odoo import models, fields
import io
import base64
import csv

class ProductKitExportWizard(models.TransientModel):
    _name = 'product.kit.export.wizard'
    _description = 'Product Kit Export Wizard'

    file = fields.Binary('Exported CSV', readonly=True)
    filename = fields.Char('Filename', readonly=True)

    def export_kits(self):
        kits = self.env['product.kits'].search([])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'id', 'product_sku', 'name', 'size', 'collection', 'color',
            'cabinet_sku', 'counter_top_sku', 'faucet_sku', 'mirror_sku'
        ])

        for kit in kits:
            writer.writerow([
                kit.id,
                kit.product_sku,
                kit.name,
                kit.size or '',
                kit.collection or '',
                kit.color or '',
                kit.cabinet_sku or '',
                kit.counter_top_sku or '',
                kit.faucet_sku or '',
                kit.mirror_sku or '',
            ])

        self.file = base64.b64encode(output.getvalue().encode('utf-8'))
        self.filename = 'product_kits_export.csv'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.kit.export.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
