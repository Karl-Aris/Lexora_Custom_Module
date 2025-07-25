from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        if not collection:
            return request.not_found()

        # Fetch kits by collection
        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        # Group kits by size
        grouped_kits = defaultdict(list)
        for kit in kits:
            grouped_kits[kit.size].append(kit)

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'grouped_kits': grouped_kits,
        })
