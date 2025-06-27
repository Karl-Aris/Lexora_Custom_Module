from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_studio_discrepancy = fields.Monetary(
        string='Discrepancy',
        compute='_compute_discrepancy',
        currency_field='x_studio_currency_id',
        store=True
    )

    x_studio_many2one_field_3d3_1iumrctbf = fields.Many2one(
        'account.move',
        string='Linked Vendor Bill',
        compute='_compute_linked_bill',
        store=True
    )

    @api.depends('x_studio_charged_amount', 'x_studio_monetary_field_782_1iumcjho4')
    def _compute_discrepancy(self):
        for rec in self:
            charged = getattr(rec, 'x_studio_charged_amount', 0.0) or 0.0
            processed = getattr(rec, 'x_studio_monetary_field_782_1iumcjho4', 0.0) or 0.0
            rec.x_studio_discrepancy = charged - processed 

    @api.depends('x_po')
    def _compute_linked_bill(self):
        for rec in self:
            bill = rec.env['account.move'].search([
                ('x_po_vb_id', '=', rec.x_po)
            ], limit=1)
            rec.x_studio_many2one_field_3d3_1iumrctbf = bill or False
