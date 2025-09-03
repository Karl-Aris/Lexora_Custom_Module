from odoo import models, fields

class ReturnReport(models.Model):
    _name = 'return.report'
    _description = 'Return Report'

    name = fields.Char(string="Report Name", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    note = fields.Text(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many(
        'return.report.line',
        'report_id',
        string="Return Lines"
    )

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
