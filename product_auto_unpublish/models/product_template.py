from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saleable = fields.Boolean(
    string="Is Saleable",
    default=True,
    help="If unchecked, product will be unpublished when out of stock."
)
    def check_and_toggle_published(self):
        for product in self.with_context(active_test=False).search([]):
            if product.qty_available <= 0 and product.website_published:
                product.website_published = False
            elif product.qty_available > 0 and not product.website_published:
                product.website_published = True


