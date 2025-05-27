from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleStockFiltered(WebsiteSale):

    def _get_shop_domain(self, search, category, attrib_values, search_in_description=True):
        _logger.warning("🧪 Using custom _get_shop_domain with stock filtering")

        domains = [request.website.sale_product_domain()]

        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)],
                ]
                if search_in_description:
                    subdomains += [
                        [('website_description', 'ilike', srch)],
                        [('description_sale', 'ilike', srch)],
                    ]
                subdomains += self._add_search_subdomains_hook(srch)
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        # ✅ Only show products if at least one variant has stock
        domains.append([('product_variant_ids.qty_available', '>', 0)])

        return expression.AND(domains)
