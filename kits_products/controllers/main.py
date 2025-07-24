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
        default_kit = kits[0]
        selected_cabinet = int(cabinet) if cabinet else (
            default_kit.cabinet_ids[0].id if default_kit.cabinet_ids else None)
        selected_counter_top = int(counter_top) if counter_top else (
            default_kit.counter_top_ids[0].id if default_kit.counter_top_ids else None)
        selected_mirror = int(mirror) if mirror else (
            default_kit.mirror_ids[0].id if default_kit.mirror_ids else None)
        selected_faucet = int(faucet) if faucet else (
            default_kit.faucet_ids[0].id if default_kit.faucet_ids else None)

    # ✅ Step 4: Find exact match for selected components
        matching_kit = None
        matching_product = None  # ✅ Ensure this is always defined

        for kit in kits:
            if selected_cabinet is not None and selected_cabinet not in kit.cabinet_ids.ids:
                continue
            if selected_counter_top is not None and selected_counter_top not in kit.counter_top_ids.ids:
                continue
            if selected_mirror is not None and selected_mirror not in kit.mirror_ids.ids:
                continue
            if selected_faucet is not None and selected_faucet not in kit.faucet_ids.ids:
                continue
            matching_kit = kit
            matching_product = kit.product_id  # ✅ Now this is safe
            break

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
        })






    @http.route(['/product_kits/group_builder'], type='http', auth="public", website=True)
    def kit_builder(self, collection=None, size=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        kits = self._get_kits(collection, size)

        # Group components by category
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

        # Filter kits based on selected components
        filtered_kits = []
        for kit in kits:
            if cabinet and int(cabinet) not in kit.cabinet_ids.ids:
                continue
            if counter_top and int(counter_top) not in kit.counter_top_ids.ids:
                continue
            if mirror and int(mirror) not in kit.mirror_ids.ids:
                continue
            if faucet and int(faucet) not in kit.faucet_ids.ids:
                continue
            filtered_kits.append(kit)

        return request.render('kits_products.kit_builder_template', {
            'kits': kits,
            'collection': collection,
            'size': size,
            'components': components,
            'cabinet': int(cabinet) if cabinet else None,
            'counter_top': int(counter_top) if counter_top else None,
            'mirror': int(mirror) if mirror else None,
            'faucet': int(faucet) if faucet else None,
            'filtered_kits': filtered_kits,
        })

    @http.route(['/product_kits/filter'], type='http', auth="public", website=True)
    def filter_kits(self, collection=None, size=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        """Filter kits by selected components."""
        kits = self._get_kits(collection, size)

        # Convert component ids to integers for comparison
        filters = {
            'cabinet': int(cabinet) if cabinet else None,
            'counter_top': int(counter_top) if counter_top else None,
            'mirror': int(mirror) if mirror else None,
            'faucet': int(faucet) if faucet else None,
        }

        filtered_kits = []

        for kit in kits:
            if filters['cabinet'] and filters['cabinet'] not in kit.cabinet_ids.ids:
                continue
            if filters['counter_top'] and filters['counter_top'] not in kit.counter_top_ids.ids:
                continue
            if filters['mirror'] and filters['mirror'] not in kit.mirror_ids.ids:
                continue
            if filters['faucet'] and filters['faucet'] not in kit.faucet_ids.ids:
                continue
            filtered_kits.append(kit)

        return request.render('kits_products.filtered_kits_template', {
            'kits': filtered_kits,
            'collection': collection,
            'size': size,
            **filters,  # Pass component selections back to the template
        })
    http.route(['/product_kits/components'], type='http', auth="public", website=True)
    def kit_components(self, **kwargs):
        """List all kit components grouped by category."""

        kits = request.env['product.kits'].sudo().search([])

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

        return request.render('kits_products.kit_components_template', {
            'components': components,
        })

    @http.route(['/product_kits/component_filter'], type='http', auth="public", website=True)
    def component_filter(self, category=None, comp_id=None, **kwargs):
        """Filter kits based on a single component selection."""

        kits = request.env['product.kits'].sudo().search([])

        matched_kits = []
        comp_id = int(comp_id)

        for kit in kits:
            if category == 'cabinet' and comp_id in kit.cabinet_ids.ids:
                matched_kits.append(kit)
            elif category == 'counter_top' and comp_id in kit.counter_top_ids.ids:
                matched_kits.append(kit)
            elif category == 'mirror' and comp_id in kit.mirror_ids.ids:
                matched_kits.append(kit)
            elif category == 'faucet' and comp_id in kit.faucet_ids.ids:
                matched_kits.append(kit)

        return request.render('kits_products.filtered_kits_template', {
            'kits': matched_kits,
            'category': category,
            'comp_id': comp_id,
        })