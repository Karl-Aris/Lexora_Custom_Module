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
        related_sizes = []
        collection_tag = ''
        color_tag = ''
        matching_product = None

        # ✅ Step 0: Ensure collection and size are provided
        if not collection or not size:
            return request.render('kits_products.kit_group_detail_template', {
                'kit': None, 'collection': collection, 'size': size,
                'components': {}, 'cabinet': None, 'counter_top': None,
                'mirror': None, 'faucet': None, 'related_sizes': []
            })

        # ✅ Step 1: Fetch kits based on collection and size
        kits = self._get_kits(collection, size)
        if not kits:
            return request.render('kits_products.kit_group_detail_template', {
                'kit': None, 'collection': collection, 'size': size,
                'components': {}, 'cabinet': None, 'counter_top': None,
                'mirror': None, 'faucet': None, 'related_sizes': []
            })

        # ✅ Step 2: Group components from kits
        components = {'cabinet': set(), 'counter_top': set(), 'mirror': set(), 'faucet': set()}
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
        for kit in kits:
            if selected_cabinet and selected_cabinet not in kit.cabinet_ids.ids:
                continue
            if selected_counter_top and selected_counter_top not in kit.counter_top_ids.ids:
                continue
            if selected_mirror and selected_mirror not in kit.mirror_ids.ids:
                continue
            if selected_faucet and selected_faucet not in kit.faucet_ids.ids:
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

        if matching_product:
            template = matching_product.product_tmpl_id
            tag_names = template.product_tag_ids.mapped('name')

            excluded_tags = [
                'Vanity Only', 'Bathroom Vanities', 'Bathroom Vanities (Cabinet)',
                'Vanity, Countertop, Sink, and Mirror', 'Vanity, Countertop, and Sink',
                'Vanity, Countertop, Sink, and Faucet', 'Vanity, Countertop, Sink, Mirror, and Faucet',
                'Single', 'Double', 'Sink', 'Countertops', 'Top', 'Acrylic', 'Frameless'
            ]

            # Get collection tag
            collection_tag = next(
                (tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags),
                None
            )
            color_tag = next(
                (tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags + [collection_tag]),
                None
            )

            tag_model = request.env['product.tag'].sudo()
            vanity_only_tag = tag_model.search([('name', '=', 'Vanity Only')])
            bv_tag = tag_model.search([('name', '=', 'Bathroom Vanities')])
            bv_cabinet_tag = tag_model.search([('name', '=', 'Bathroom Vanities (Cabinet)')])
            collection_tag_obj = tag_model.search([('name', '=', collection_tag)]) if collection_tag else None
            color_tag_obj = tag_model.search([('name', '=', color_tag)]) if color_tag else None

            # ✅ Fetch related sizes
            if vanity_only_tag and (bv_tag or bv_cabinet_tag) and collection_tag_obj and color_tag_obj:
                candidate_templates = request.env['product.template'].sudo().search([
                    ('product_tag_ids', 'in', [
                        vanity_only_tag.id, collection_tag_obj.id, color_tag_obj.id
                    ])
                ])

                def matches_required_tags(template):
                    tags = template.product_tag_ids
                    return (
                        vanity_only_tag in tags and
                        (bv_tag in tags or bv_cabinet_tag in tags) and
                        collection_tag_obj in tags and
                        color_tag_obj in tags
                    )

                size_templates = candidate_templates.filtered(matches_required_tags)
                related_sizes = request.env['product.product'].sudo().search([
                    ('product_tmpl_id', 'in', size_templates.ids)
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
            'related_sizes': related_sizes,
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
     


