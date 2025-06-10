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
        string="With Stock Not Published",
        default=False,
        help="If checked, product will NOT be published even if it has stock."
    )

    def check_and_toggle_published(self):
        _logger.info("Running product website publish toggle for 20 products...")
    
        products = self.with_context(active_test=False).search([], limit=20)
    
        for product in products:
            qty = product.qty_available
            published = product.website_published
            saleable = product.is_saleable
            blocked = product.with_stock_not_published
    
            if blocked and published:
                product.website_published = False
                _logger.info(f"Unpublished (blocked): [{product.default_code}] {product.name} (Qty: {qty})")
            elif not saleable and qty <= 0 and published:
                product.website_published = False
                _logger.info(f"Unpublished (no stock & not saleable): [{product.default_code}] {product.name} (Qty: {qty})")
            elif (qty > 0 or saleable) and not published:
                product.website_published = True
                _logger.info(f"Published: [{product.default_code}] {product.name} (Qty: {qty})")
    
        _logger.info("Finished toggling publish status for 20 products.")
