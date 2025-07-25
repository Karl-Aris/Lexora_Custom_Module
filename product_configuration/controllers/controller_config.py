from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        selected_sku = kwargs.get('cabinet_sku')

        if not collection:
            return request.not_found()

        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        size_cards = []
        seen_sizes = set()

        for kit in kits:
            size = kit.size
            cabinet_sku = kit.cabinet_sku

            if size in seen_sizes:
                continue
            seen_sizes.add(size)

            product = request.env['product.product'].sudo().search([('default_code', '=', cabinet_sku)], limit=1)

            size_cards.append({
                'size': size,
                'cabinet_sku': cabinet_sku,
                'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
            })

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'selected_sku': selected_sku,
            'size_cards': size_cards,
        })
