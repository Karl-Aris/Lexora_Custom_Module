from odoo import models, fields

class ReturnReport(models.Model):
    _name = 'return.report'
    _description = 'Return Report'

    name = fields.Char(string="Return Reference", required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('return.report'))
    date = fields.Date(string="Return Date", default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="Status", default='draft')
    note = fields.Text(string="Notes")

    line_ids = fields.One2many('return.report.line', 'report_id', string="Return Lines")

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})
