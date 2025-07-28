from odoo import models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_vendor_bill(self):
        # Placeholder logic: you can customize this later
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Vendor Bill'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'in_invoice',
                'default_invoice_origin': self.name,
            }
        }
