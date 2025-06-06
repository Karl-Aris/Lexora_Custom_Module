from odoo import models, api
import logging

_logger = logging.getLogger(name)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def check_and_toggle_published(self):
        for product in self.with_context(active_test=False).search([]):
            if not product.is_saleable:
                # Always unpublish non-sellable products
                if product.website_published:
                    product.website_published = False
                    _logger.info(f"Unpublished non-sellable product: {product.name}")
                continue

            # Publish or unpublish sellable products based on stock
            if product.qty_available <= 0 and product.website_published:
                product.website_published = False
                _logger.info(f"Unpublished due to no stock: {product.name}")
            elif product.qty_available > 0 and not product.website_published:
                product.website_published = True
                _logger.info(f"Published sellable product with stock: {product.name}")
