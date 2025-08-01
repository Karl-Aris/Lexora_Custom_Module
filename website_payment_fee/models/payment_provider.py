from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _remove_existing_fee_line(self):
        fee_product = self.env.ref("product.product_product_consultant", raise_if_not_found=False)
        if not fee_product:
            return
        self.order_line.filtered(lambda l: l.product_id == fee_product).unlink()

    def _add_authorize_net_fee_line(self):
        fee_product = self.env.ref("product.product_product_consultant", raise_if_not_found=False)
        if not fee_product:
            return
        self._remove_existing_fee_line()
        self.order_line.create({
            'order_id': self.id,
            'product_id': fee_product.id,
            'name': fee_product.name,
            'product_uom_qty': 1,
            'product_uom': fee_product.uom_id.id,
            'price_unit': fee_product.list_price,
        })

    @api.model
    def create(self, vals):
        order = super().create(vals)
        if order.payment_provider_id.code == "authorize":
            order._add_authorize_net_fee_line()
        return order

    def write(self, vals):
        res = super().write(vals)
        if "payment_provider_id" in vals:
            for order in self:
                if order.payment_provider_id.code == "authorize":
                    order._add_authorize_net_fee_line()
                else:
                    order._remove_existing_fee_line()
        return res
