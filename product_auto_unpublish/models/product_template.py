from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def check_and_toggle_published(self):
        products = self.with_context(active_test=False).search([])

        for product in products:
            qty = sum(product.product_variant_ids.mapped('qty_available'))
            published = product.website_published

            _logger.info(f"[Stock Check] Product: {product.name} | Qty: {qty} | Published: {published}")

            if qty <= 0 and published:
                product.website_published = False
                _logger.info(f"→ Unpublished: {product.name} (Out of stock)")
            elif qty > 0 and not published:
                product.website_published = True
                _logger.info(f"→ Published: {product.name} (Back in stock)")
