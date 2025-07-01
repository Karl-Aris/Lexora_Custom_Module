from odoo import api, fields, models
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    merchant = fields.Char(string="Merchant")
    sku = fields.Char(string="SKU")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    picking_id = fields.Many2one('stock.picking', string="Incoming Picking")
    tracking_bol = fields.Char(string="Tracking/BOL")
    carrier = fields.Char(string="Carrier")
    return_amount = fields.Monetary(string="Return Amount")
    currency_id = fields.Many2one('res.currency', string='Currency')
    condition_reported = fields.Selection([
        ('good', 'Good'),
        ('damaged_filed', 'Damaged/Filed')
    ], string="Condition Reported")
    sign_bol = fields.Boolean(string="Sign BOL")
    initials = fields.Char(string="Initials")

    def action_return_to_vendor(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError("No incoming picking is linked to this ticket.")

        return {
            'name': 'Return to Vendor',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.return.picking',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.picking_id.id,
                'active_model': 'stock.picking',
            }
        }
