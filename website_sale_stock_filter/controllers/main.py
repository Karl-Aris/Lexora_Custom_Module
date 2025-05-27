from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleStockFilter(WebsiteSale):
    def _shop_get_product_domain(self, search, category, attrib_values):
        domain = super()._shop_get_product_domain(search, category, attrib_values)
        if domain is not None:
        domain += [('product_variant_ids.qty_available', '>', 0)]

        return domain
