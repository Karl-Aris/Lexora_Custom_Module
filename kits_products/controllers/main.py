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
        collection = kwargs.get('collection')
        size = kwargs.get('size')
 
        attribute_value = request.env['product.template.attribute.value'].sudo().search([
            ('name', '=', 'Bathroom Vanity')
        ], limit=1)

        product_templates = request.env['product.template'].sudo().search([
            ('attribute_line_ids.value_ids', 'in', attribute_value.ids)
        ])
 
        if collection:
            product_templates = product_templates.filtered(lambda p: p.x_collection == collection)
        if size:
            product_templates = product_templates.filtered(lambda p: p.x_size == size)
 
        products = request.env['product.product'].sudo().search([
            ('product_tmpl_id', 'in', product_templates.ids)
        ])

        return request.render('kits_products.all_products_template', {
            'products': products,
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
        product_specs = {}
        if matching_product:
            # Variant-level attributes (product.product)
            product_specs['variant_attributes'] = [{
            'attribute': val.attribute_id.name,
            'value': val.product_attribute_value_id.name,
            } for val in matching_product.product_template_attribute_value_ids]


            # Template-level attributes (product.template)
            tmpl = matching_product.product_tmpl_id
            product_specs['template_attributes'] = [{
                'attribute': line.attribute_id.name,
                'values': [v.name for v in line.value_ids],
            } for line in tmpl.attribute_line_ids]

            # Custom specs or fields
            product_specs['description_sale'] = tmpl.description_sale
            product_specs['description'] = tmpl.description
            product_specs['x_specifications'] = tmpl.x_specifications if hasattr(tmpl, 'x_specifications') else ''
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
            'product_specs': product_specs,  # ✅ Pass the specs to template
        })
