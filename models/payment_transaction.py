from odoo import models, api

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)
        for tx in transactions:
            if tx.provider_id.code == 'authorize':
                tx._add_authorize_surcharge()
        return transactions

    def _add_authorize_surcharge(self):
        sale_order = self.sale_order_id
        if not sale_order:
            return

        # Avoid adding surcharge multiple times
        if any(line.name == 'Authorize.Net Surcharge' for line in sale_order.order_line):
            return

        # Calculate 3% surcharge
        surcharge_percent = 3.0
        surcharge_amount = sale_order.amount_total * (surcharge_percent / 100)

        # Load product via XML ID or product name
        surcharge_product = self.env['product.product'].search([('name', '=', 'Authorize.Net Surcharge')], limit=1)

        if not surcharge_product:
            return  # Avoid error if product doesn't exist

        # Create the surcharge line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': surcharge_product.id,
            'name': 'Authorize.Net Surcharge',
            'product_uom_qty': 1,
            'price_unit': round(surcharge_amount, 2),
        })
