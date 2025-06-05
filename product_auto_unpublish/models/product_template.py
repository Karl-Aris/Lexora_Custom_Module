
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._check_stock_and_publish()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._check_stock_and_publish()
        return res

    def _check_stock_and_publish(self):
        for product in self:
            if product.qty_available <= 0 and product.website_published:
                product.website_published = False
            elif product.qty_available > 0 and not product.website_published:
                product.website_published = True
