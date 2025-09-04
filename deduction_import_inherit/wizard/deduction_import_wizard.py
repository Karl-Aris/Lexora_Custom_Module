
from odoo import models, fields
import base64, io, csv

class DeductionImportWizard(models.TransientModel):
    _name = "deduction.import.wizard"
    _description = "Deduction Import Wizard"

    file_data = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")

    def action_import(self):
        if not self.file_data:
            return
        data = base64.b64decode(self.file_data)
        file_input = io.StringIO(data.decode("utf-8"))
        reader = csv.DictReader(file_input)

        for row in reader:
            deduction = self.env["deduction.vendor"].create({
                "name": row.get("Deduction #"),
                "partner_id": int(row.get("Customer") or 0),
                "purchase_order": row.get("PO #"),
                "deduction_date": row.get("Deduction Date"),
                "deduction_total_amount": row.get("Deduction Total Amount"),
                "reason": row.get("Reason"),
                "ticket_status": row.get("Ticket Status"),
            })
            if row.get("SKU"):
                self.env["deduction.vendor.line"].create({
                    "deduction_id": deduction.id,
                    "sku_id": int(row.get("SKU") or 0),
                    "po_number": row.get("PO Number"),
                    "amount": row.get("Amount"),
                })
