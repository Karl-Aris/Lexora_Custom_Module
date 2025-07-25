# controllers/main.py

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

        # Build list of sizes with associated product image
        size_cards = []
        seen_sizes = set()

        for kit in kits:
            size = kit.size
            sku = kit.sku  # Adjust this field if your SKU field has a different name

            if size in seen_sizes:
                continue
            seen_sizes.add(size)

            # Try to fetch matching product by default_code (SKU)
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            size_cards.append({
                'size': size,
                'image': product.image_1920 if product else None
            })

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'size_cards': size_cards,
        })
