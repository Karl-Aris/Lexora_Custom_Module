from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def check_and_toggle_published(self):
    for product in self.with_context(active_test=False).search([]):
        qty = product.qty_available
        published = product.website_published

        # Respect is_saleable flag
        if not product.is_saleable and qty <= 0 and published:
            product.website_published = False
        elif (qty > 0 or product.is_saleable) and not published:
            product.website_published = True

