from odoo import models, fields

class ReturnOrder(models.Model):
    _name = 'return.order'
    _description = 'Return Order'

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="New")
    partner_id = fields.Many2one('res.partner', string="Customer")
    picking_id = fields.Many2one('stock.picking', string="Related Picking")
    state = fields.Selection([
        ('initiated', 'Return Initiated'),
        ('returned', 'Returned'),
    ], string="Status", default='initiated')
    x_location = fields.Char(string="Location")

    def action_mark_returned(self):
        for rec in self:
            rec.state = 'returned'
