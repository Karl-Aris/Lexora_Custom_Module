import logging
_logger = logging.getLogger(__name__)

def _shop_get_product_search_domain(self, search, category, attrib_values):
    _logger.info(f"Filtering by availability: {request.params.get('availability')}")
    domain = super()._shop_get_product_search_domain(search, category, attrib_values)
    availability = request.params.get('availability')
    if availability == 'available':
        domain += [('inventory_quantity_auto_apply', '>', 0)]
    elif availability == 'not_available':
        domain += [('inventory_quantity_auto_apply', '<=', 0)]
    return domain
