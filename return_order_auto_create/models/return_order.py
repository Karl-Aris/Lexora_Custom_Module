from odoo import models, fields, api

class ReturnOrder(models.Model):
    _name = 'return.order'
    _description = 'Return Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='set null')
    partner_id = fields.Many2one('res.partner', string='Customer', ondelete='set null')
    picking_id = fields.Many2one('stock.picking', string='Related Picking', ondelete='set null')
    state = fields.Selection([('initiated', 'Return Initiated'), ('returned', 'Returned')], string='Status', default='initiated')

    @api.model
    def create(self, vals):
        # ensure unique readable name if default 'New'
        if vals.get('name', 'New') in (None, '', 'New'):
            seq = self.env['ir.sequence'].sudo().next_by_code('return.order') or 'RET'
            vals['name'] = seq
        return super(ReturnOrder, self).create(vals)

    def action_mark_returned(self):
        for rec in self:
            rec.state = 'returned'
