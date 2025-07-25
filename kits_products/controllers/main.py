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
        """List all kits grouped by collection and size."""
        kits = request.env['product.kits'].sudo().search([])

        grouped_kits = defaultdict(list)
        for kit in kits:
            key = (kit.collection, kit.size)
            grouped_kits[key].append(kit)

        return request.render('kits_products.kits_list_template', {
            'grouped_kits': dict(grouped_kits),
        })
    

    @http.route(['/all_products'], type='http', auth="public", website=True)
    def list_all_products(self, **kwargs):
        # You can pass these via query string or hardcode for now
        collection = kwargs.get('collection')
        size = kwargs.get('size')

        tag_names = ['Bathroom Vanities']
        if collection:
            tag_names.append(collection)
        if size:
            tag_names.append(size)

        # Search for product templates with matching tags
        tags = request.env['product.tag'].sudo().search([('name', 'in', tag_names)])
        product_templates = request.env['product.template'].sudo().search([
            ('product_tag_ids', 'in', tags.ids)
        ])

        # Now get products linked to those templates
        products = request.env['product.product'].sudo().search([
            ('product_tmpl_id', 'in', product_templates.ids)
        ])

        return request.render('kits_products.all_products_template', {
            'products': products,
        })

    @http.route(['/product_kits/group'], type='http', auth="public", website=True)
    def group_detail(self, collection=None, size=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        """Display a single matching kit (by collection and size) and filterable components."""

    # ✅ Step 0: Ensure collection and size are provided
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
            })

    # ✅ Step 1: Fetch kits based on collection and size
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
            })

    # ✅ Step 2: Group components from kits
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

    # ✅ Step 3: Determine selected components
        default_kit = kits[0]  # Always define default kit

        # Determine if it's the first load (no selections at all)
        is_first_load = not any([cabinet, counter_top, mirror, faucet])

        # Use default values only if it's the first load
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
        # ✅ Step 4: Find exact match for selected components ONLY
        matching_kit = None
        matching_product = None

        for kit in kits:
            # Skip if selected component is not in the kit
            if selected_cabinet is not None and selected_cabinet not in kit.cabinet_ids.ids:
                continue
            if selected_counter_top is not None and selected_counter_top not in kit.counter_top_ids.ids:
                continue
            if selected_mirror is not None and selected_mirror not in kit.mirror_ids.ids:
                continue
            if selected_faucet is not None and selected_faucet not in kit.faucet_ids.ids:
                continue

            # ✅ NEW: skip kits that have extra components not selected
            if selected_cabinet is None and kit.cabinet_ids:
                continue
            if selected_counter_top is None and kit.counter_top_ids:
                continue
            if selected_mirror is None and kit.mirror_ids:
                continue
            if selected_faucet is None and kit.faucet_ids:
                continue

            # ✅ This kit exactly matches the selected components (and no extras)
            matching_kit = kit
            matching_product = kit.product_id
            break
         # ✅ Step 5: Find related products with same tags and color
                # ✅ Step 5: Find related products using collection and color as tag names
                # ✅ Step 5: Find related products using collection and color as tag names
        related_products = []
        if matching_product:
            tag_model = request.env['product.tag'].sudo()
            collection_tag_obj = tag_model.search([('name', '=', collection)]) if collection else None
            color_tag_obj = tag_model.search([('name', '=', matching_kit.color)]) if matching_kit.color else None

            tag_ids = []
            if collection_tag_obj:
                tag_ids.append(collection_tag_obj.id)
            if color_tag_obj:
                tag_ids.append(color_tag_obj.id)

            if tag_ids:
                related_products = request.env['product.product'].sudo().search([
                    ('id', '!=', matching_product.id),
                    ('o_product_tags', 'in', tag_ids),
                ])

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
            'related_products': related_products,
        })


        
    