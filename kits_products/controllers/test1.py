from odoo import http
from odoo.http import request
from collections import defaultdict

class TestController(http.Controller):

    def _get_kits(self, collection=None, size=None):
        """Helper to get kits by collection and optional size."""
        domain = [('collection', '=', collection)]
        if size:
            domain.append(('size', '=', size))
        else:
            domain.append(('size', '=', False))
        return request.env['product.kits'].sudo().search(domain)

    @http.route(['/product_kits'], type='http', auth="public", website=True)
    def list_kits(self, **kwargs):
        collection_filter = kwargs.get('collection', '').strip()
        size_filter = kwargs.get('size', '').strip()
        color_filter = kwargs.get('color', '').strip()
        sort_key = kwargs.get('sort')
        page = int(kwargs.get('page', 1))
        per_page = 12

        domain = []
        if collection_filter:
            domain.append(('collection', '=', collection_filter))
        if size_filter:
            domain.append(('size', '=', size_filter))
        if color_filter:
            domain.append(('color', '=', color_filter))

        kits_model = request.env['product.kits'].sudo()
        kits = kits_model.search(domain)
 
        all_kits = kits_model.search([])
        collections = sorted(set(k.collection for k in all_kits if k.collection))
        sizes = sorted(set(k.size for k in all_kits if k.size))
        colors = sorted(set(k.color for k in all_kits if k.color))
 
        from collections import defaultdict
        grouped = defaultdict(list)
        for kit in kits:
            key = (kit.collection, kit.size)
            grouped[key].append(kit)

        unique_kits = [kits[0] for kits in grouped.values()]
 
        if sort_key == 'collection':
            unique_kits.sort(key=lambda k: k.collection or '')
        elif sort_key == 'size':
            unique_kits.sort(key=lambda k: k.size or '')
        elif sort_key == 'color':
            unique_kits.sort(key=lambda k: k.color or '')
 
        start = (page - 1) * per_page
        end = start + per_page
        paged_kits = unique_kits[start:end]
        total_pages = (len(unique_kits) + per_page - 1) // per_page   

        return request.render('kits_products.kits_list_template', {
            'paged_kits': paged_kits,
            'page': page,
            'has_next': end < len(unique_kits),
            'collection': collection_filter,
            'size': size_filter,
            'color': color_filter,
            'sort': sort_key,
            'collections': collections,
            'sizes': sizes,
            'colors': colors,
            'total_pages': total_pages,  
        })
 