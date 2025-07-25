from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        if not collection:
            return request.not_found()

        # Fetch kits in the collection
        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        # Build list of sizes with associated product image from product.product via SKU
        size_cards = []
        seen_sizes = set()

        for kit in kits:
            size = kit.size
            sku = kit.cabinet_sku  # adjust field name if needed

            if size in seen_sizes:
                continue
            seen_sizes.add(size)

            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            size_cards.append({
                'size': size,
                'image': product.image_1920 if product else None
            })

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'size_cards': size_cards,
        })
