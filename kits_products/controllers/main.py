from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductKitsController(http.Controller):

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
        per_page = 8

        domain = []
        if collection_filter:
            domain.append(('collection', '=', collection_filter))
        if size_filter:
            domain.append(('size', '=', size_filter))
        if color_filter:
            domain.append(('color', '=', color_filter))

        kits_model = request.env['product.kits'].sudo()
        kits = kits_model.search(domain)

        # 🔍 Distinct dropdown values
        all_kits = kits_model.search([])
        collections = sorted(set(k.collection for k in all_kits if k.collection))
        sizes = sorted(set(k.size for k in all_kits if k.size))
        colors = sorted(set(k.color for k in all_kits if k.color))

        # 🧱 Group kits by (collection, size) as unique identifier
        from collections import defaultdict
        grouped = defaultdict(list)
        for kit in kits:
            key = (kit.collection, kit.size)
            grouped[key].append(kit)

        unique_kits = [kits[0] for kits in grouped.values()]

        # 🔃 Sorting
        if sort_key == 'collection':
            unique_kits.sort(key=lambda k: k.collection or '')
        elif sort_key == 'size':
            unique_kits.sort(key=lambda k: k.size or '')
        elif sort_key == 'color':
            unique_kits.sort(key=lambda k: k.color or '')

        # 📄 Pagination
        # 📄 Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paged_kits = unique_kits[start:end]
        total_pages = (len(unique_kits) + per_page - 1) // per_page  # ceiling division

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
            'total_pages': total_pages,  # NEW
        })

 


 

    @http.route(['/product_kits/group'], type='http', auth="public", website=True)
    def group_detail(self, collection=None, size=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        """Display a single matching kit (by collection and size) and filterable components."""
 
        if not collection or not size:
            return request.render('kits_products.kit_group_detail_template', {
                'kit': None,
                'collection': collection,
                'size': size,
                'components': {},
                'cabinet': None,
                'counter_top': None,
                'mirror': None,
                'faucet': None,
                'related_kits': [],
            })
 
        kits = self._get_kits(collection, size)
        if not kits:
            return request.render('kits_products.kit_group_detail_template', {
                'kit': None,
                'collection': collection,
                'size': size,
                'components': {},
                'cabinet': None,
                'counter_top': None,
                'mirror': None,
                'faucet': None,
                'related_kits': [],
            })
 
        components = {
            'cabinet': set(),
            'counter_top': set(),
            'mirror': set(),
            'faucet': set(),
        }
        for kit in kits:
            components['cabinet'].update(kit.cabinet_ids)
            components['counter_top'].update(kit.counter_top_ids)
            components['mirror'].update(kit.mirror_ids)
            components['faucet'].update(kit.faucet_ids)
 
        default_kit = kits[0]
        is_first_load = not any([cabinet, counter_top, mirror, faucet])

        selected_cabinet = int(cabinet) if cabinet else (
            default_kit.cabinet_ids[0].id if default_kit.cabinet_ids and is_first_load else None
        )
        selected_counter_top = int(counter_top) if counter_top else (
            default_kit.counter_top_ids[0].id if default_kit.counter_top_ids and is_first_load else None
        )
        selected_mirror = int(mirror) if mirror else (
            default_kit.mirror_ids[0].id if default_kit.mirror_ids and is_first_load else None
        )
        selected_faucet = int(faucet) if faucet else (
            default_kit.faucet_ids[0].id if default_kit.faucet_ids and is_first_load else None
        )

        # ✅ Step 4: Find exact match for selected components
        matching_kit = None
        matching_product = None

        for kit in kits:
            if selected_cabinet is not None and selected_cabinet not in kit.cabinet_ids.ids:
                continue
            if selected_counter_top is not None and selected_counter_top not in kit.counter_top_ids.ids:
                continue
            if selected_mirror is not None and selected_mirror not in kit.mirror_ids.ids:
                continue
            if selected_faucet is not None and selected_faucet not in kit.faucet_ids.ids:
                continue

            if selected_cabinet is None and kit.cabinet_ids:
                continue
            if selected_counter_top is None and kit.counter_top_ids:
                continue
            if selected_mirror is None and kit.mirror_ids:
                continue
            if selected_faucet is None and kit.faucet_ids:
                continue

            matching_kit = kit
            matching_product = kit.product_id
            break
 
        related_kits = []
        if matching_kit and matching_kit.color and matching_kit.collection:
            all_related_kits = request.env['product.kits'].sudo().search([
                ('id', '!=', matching_kit.id),
                ('color', '=', matching_kit.color),
                ('collection', '=', matching_kit.collection),
            ])
 
            seen_sizes = set()
            unique_related_kits = []
            for kit in all_related_kits:
                if kit.size and kit.size not in seen_sizes:
                    seen_sizes.add(kit.size)
                    unique_related_kits.append(kit)
            related_kits = unique_related_kits
        
        return request.render('kits_products.kit_group_detail_template', {
            'kit': matching_kit,
            'product': matching_product,
            'collection': collection,
            'size': size,
            'components': components,
            'cabinet': selected_cabinet,
            'counter_top': selected_counter_top,
            'mirror': selected_mirror,
            'faucet': selected_faucet,
            'related_kits': related_kits,   
        })