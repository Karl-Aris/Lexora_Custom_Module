from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _add_payment_fee_line(self):
        fee_product = self.env.ref('website_payment_fee.product_authorize_net_fee', raise_if_not_found=False)
        if not fee_product:
            return

        for line in self.order_line:
            if line.product_id == fee_product:
                return  # already added

        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': fee_product.name,
            'product_uom_qty': 1,
            'product_uom': fee_product.uom_id.id,
            'price_unit': fee_product.lst_price,
        })
