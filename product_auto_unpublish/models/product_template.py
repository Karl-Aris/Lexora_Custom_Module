from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saleable = fields.Boolean(
        string="Is Saleable",
        default=True,
        help="If checked, product will remain published even when out of stock."
    )

    def check_and_toggle_published(self):
    _logger.info("Running product website publish toggle based on stock...")

    # Only fetch relevant products
    products = self.with_context(active_test=False).search([
        '|', ('qty_available', '<=', 0), ('website_published', '=', False)
    ])

    for product in products:
        qty = product.qty_available
        published = product.website_published
        saleable = product.is_saleable

        if not saleable and qty <= 0 and published:
            product.website_published = False
            _logger.info(f"Unpublished: [{product.default_code}] {product.name} (Qty: {qty})")
        elif (qty > 0 or saleable) and not published:
            product.website_published = True
            _logger.info(f"Published: [{product.default_code}] {product.name} (Qty: {qty})")

    _logger.info("Completed product website publish toggle.")

