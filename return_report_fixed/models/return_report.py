from odoo import models, fields

class ReturnReport(models.Model):
    _name = "return.report"
    _description = "Return Report"

    name = fields.Char(string="Reference", required=True)
    date = fields.Date(string="Return Date")
    note = fields.Text(string="Notes")

    # Status bar field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="Status", default='draft')
