from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        if not collection:
            return request.not_found()

        # Get all kits in this collection
        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        # Extract unique sizes
        sizes = sorted(set(kits.mapped('size')))

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'sizes': sizes,
            'kits': kits,
        })
