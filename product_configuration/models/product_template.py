from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    with_stock_not_published = fields.Boolean(
        string="With Stock But Not Published",
        default=False,
        help="If checked, product will NOT be published on the website even if it has stock."
    )

    def check_and_toggle_published(self):
        _logger.info("Running product website publish toggle...")
        products = self.with_context(active_test=False).search([])  # All products

        for product in products:
            qty = product.qty_available
            published = product.website_published
            stock_not_pub = product.with_stock_not_published

            # If product is marked to not show on website even if stock available, unpublish it
            if stock_not_pub and qty > 0 and published:
                product.website_published = False
                _logger.info(f"Unpublished due to with_stock_not_published: [{product.default_code}] {product.name} (Qty: {qty})")

            # Normal logic: publish if has stock and not already published
            elif not stock_not_pub:
                if qty <= 0 and published:
                    product.website_published = False
                    _logger.info(f"Unpublished (out of stock): [{product.default_code}] {product.name} (Qty: {qty})")
                elif qty > 0 and not published:
                    product.website_published = True
                    _logger.info(f"Published: [{product.default_code}] {product.name} (Qty: {qty})")

        _logger.info("Finished toggling publish status.")

