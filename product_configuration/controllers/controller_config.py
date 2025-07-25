# controllers/main.py

from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductKitsController(http.Controller):

    @http.route(['/kits/<string:collection>'], type='http', auth='public', website=True)
    def kits_by_collection(self, collection, **kwargs):
        # Fetch product.kits records matching collection
        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        # Group by size
        grouped_kits = defaultdict(list)
        for kit in kits:
            grouped_kits[kit.size].append(kit)

        # Send to template
        return request.render('your_module.kits_template', {
            'collection': collection,
            'grouped_kits': grouped_kits,
        })
