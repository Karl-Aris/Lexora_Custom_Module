from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saleable = fields.Boolean(
        string="Is Saleable",
        default=True,
        help="If checked, product will remain published even when out of stock."
    )

    def check_and_toggle_published(self):
        products = self.with_context(active_test=False).search([])
        for product in products:
            qty = product.qty_available
            published = product.website_published
            saleable = product.is_saleable

            if not saleable and qty <= 0 and published:
                product.website_published = False
                _logger.info("Unpublished: %s (Qty: %s)", product.display_name, qty)
            elif (qty > 0 or saleable) and not published:
                product.website_published = True
                _logger.info("Published: %s (Qty: %s)", product.display_name, qty)
