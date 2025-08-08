from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _extract_ids(self, commands):
        ids = []
        for command in commands:
            if isinstance(command, int):
                ids.append(command)
            elif isinstance(command, (list, tuple)) and len(command) == 3:
                if command[0] == 6:
                    ids.extend(command[2])
                elif command[0] == 4:
                    ids.append(command[1])
        return ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'sale_order_ids' in vals:
                so_commands = vals['sale_order_ids']
                so_ids = self._extract_ids(so_commands)
                if so_ids:
                    sale_orders = self.env['sale.order'].browse(so_ids)
                    sale_orders._add_authorize_net_fee()

        return super().create(vals_list)
