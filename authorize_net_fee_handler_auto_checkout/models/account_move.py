from odoo import models, fields, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def apply_authorize_net_fee(self, transaction):
        self.ensure_one()
        if self.move_type != 'out_invoice' or self.state != 'posted':
            return

        if not transaction or transaction.provider_id.code != 'authorize':
            return

        if any(line.product_id.default_code == 'AUTH_NET_FEE' for line in self.invoice_line_ids):
            return

        fee_product = self.env['product.product'].search([('default_code', '=', 'AUTH_NET_FEE')], limit=1)
        if not fee_product:
            raise UserError(_("Product with Internal Reference 'AUTH_NET_FEE' not found."))

        fee_amount = self.amount_total * 0.03

        self.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': fee_product.id,
                'quantity': 1,
                'price_unit': fee_amount,
                'name': _('Authorize.Net 3% Surcharge'),
            })]
        })
