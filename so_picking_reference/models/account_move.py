from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_sale_order_from_vendor_bill()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_sale_order_from_vendor_bill()
        return res

    def _update_sale_order_from_vendor_bill(self):
        for rec in self:
            if (
                rec.move_type == 'in_invoice' and
                rec.sale_order_id and
                rec.name != '/'
            ):
                rec.sale_order_id.write({
                    'x_vb_number': rec.name,
                    'x_amount': rec.amount_total_signed,
                    'x_bol' : rec.ref,
                    'x_vb_date' : rec.invoice_date,
                })
