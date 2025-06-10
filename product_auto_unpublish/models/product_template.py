from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saleable = fields.Boolean(
        string="Is Saleable",
        default=True,
        help="If checked, product will remain published even when out of stock."
    )

    with_stock_not_published = fields.Boolean(
        string="With Stock But Not Published",
        default=False,
        help="If checked, product will NOT be published on the website even if it has stock."
    )

    def check_and_toggle_published(self):
        _logger.info("Running product website publish toggle...")

        products = self.with_context(active_test=False).search([])  # no limit if you want all products

        for product in products:
            qty = product.qty_available
            published = product.website_published
            saleable = product.is_saleable
            stock_not_pub = product.with_stock_not_published

            # If product is marked to not show on website even if stock available, unpublish it
            if stock_not_pub and qty > 0 and published:
                product.website_published = False
                _logger.info(f"Unpublished due to with_stock_not_published: [{product.default_code}] {product.name} (Qty: {qty})")

            # If product is NOT marked with_stock_not_published, apply normal logic:
            elif not stock_not_pub:
                if not saleable and qty <= 0 and published:
                    product.website_published = False
                    _logger.info(f"Unpublished (out of stock and not saleable): [{product.default_code}] {product.name} (Qty: {qty})")
                elif (qty > 0 or saleable) and not published:
                    product.website_published = True
                    _logger.info(f"Published: [{product.default_code}] {product.name} (Qty: {qty})")

        _logger.info("Finished toggling publish status.")
