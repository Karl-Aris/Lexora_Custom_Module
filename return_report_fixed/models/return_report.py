from odoo import models, fields

class ReturnReport(models.Model):
    _name = 'return.report'
    _description = 'Return Report'

    name = fields.Char(string="Report Reference", required=True, copy=False, readonly=True,
                       default="New")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    note = fields.Text(string="Notes")
    line_ids = fields.One2many('return.report.line', 'report_id', string="Return Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string="Status", default='draft', tracking=True)

    def action_confirm(self):
        """Move report to Confirmed state"""
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        """Move report to Done state"""
        for rec in self:
            rec.state = 'done'

    # Optional: auto-generate sequence for name
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('return.report') or "New"
        return super().create(vals)
