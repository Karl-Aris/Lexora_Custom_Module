from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        # Before creating transaction, add surcharge lines to related SOs
        for vals in vals_list:
            # You must adjust this depending on your data model
            # Common way: the transaction may have reference to sale order via 'reference' or 'sale_order_ids'
            # Here we assume sale_order_ids is populated (adjust if necessary)
            if 'sale_order_ids' in vals:
                so_ids = vals['sale_order_ids']
                if so_ids:
                    sale_orders = self.env['sale.order'].browse(so_ids)
                    sale_orders._add_authorize_net_fee()

        return super().create(vals_list)
