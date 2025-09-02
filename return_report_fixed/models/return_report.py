from odoo import models, fields, api

class ReturnReport(models.Model):
    _name = "return.report"
    _description = "Return Report"

    name = fields.Char(string="Report Name", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    note = fields.Text(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
