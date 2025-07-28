from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        selected_collection = kwargs.get('collection')
        selected_color = kwargs.get('color')
        selected_sku = kwargs.get('cabinet_sku')
        selected_countertop = kwargs.get('counter_top_sku')
        selected_mirror = kwargs.get('mirror_sku')
        selected_faucet = kwargs.get('faucet_sku')
        
        configured_kit = None
        configured_product = None

        # Step 1: Load collections
        collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        unique_collections = sorted(set(collections))

        kits = request.env['product.kits'].sudo().search([])
        if selected_collection:
            kits = kits.filtered(lambda k: k.collection == selected_collection)

        # Step 2: Get colors for the selected collection
        colors = sorted(set(kit.color.strip().lower() for kit in kits if kit.color))
        distinct_colors = []
        seen_colors = set()
        
        for color in colors:
            original_color = next((kit.color for kit in kits if kit.color.strip().lower() == color), None)
            if original_color and original_color.lower() not in seen_colors:
                distinct_colors.append(original_color)
                seen_colors.add(original_color.lower())
                
        selected_color_normalized = selected_color.lower() if selected_color else None
        if selected_color:
            kits = kits.filtered(lambda k: k.color and k.color.lower() == selected_color_normalized)

        # Step 3: Collect unique cabinet sizes/cards
        seen_sizes = set()
        size_cards = []
        for kit in kits:
            if kit.size and kit.size.strip().lower() not in seen_sizes:
                seen_sizes.add(kit.size.strip().lower())
                product = request.env['product.product'].sudo().search([('default_code', '=', kit.cabinet_sku)], limit=1)
                size_cards.append({
                    'size': kit.size,
                    'cabinet_sku': kit.cabinet_sku,
                    'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                })

        size_cards.sort(key=lambda x: float(x['size']))

        # Step 4: Filter kits based on selected components
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []
        if selected_sku:
            matching_kits = kits.filtered(lambda k: k.cabinet_sku == selected_sku)

            seen_ctops, seen_mirrors, seen_faucets = set(), set(), set()
            for kit in matching_kits:
                if kit.counter_top_sku and kit.counter_top_sku not in seen_ctops:
                    seen_ctops.add(kit.counter_top_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.counter_top_sku)], limit=1)
                    counter_top_cards.append({
                        'counter_top_sku': kit.counter_top_sku,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })

                if kit.mirror_sku and kit.mirror_sku not in seen_mirrors:
                    seen_mirrors.add(kit.mirror_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.mirror_sku)], limit=1)
                    mirror_cards.append({
                        'mirror_sku': kit.mirror_sku,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })

                if kit.faucet_sku and kit.faucet_sku not in seen_faucets:
                    seen_faucets.add(kit.faucet_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.faucet_sku)], limit=1)
                    faucet_cards.append({
                        'faucet_sku': kit.faucet_sku,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })

        # Step 5: Configure the selected kit if more than one component is selected
        configured_kit = None
        configured_product = None

        # Start with a base domain (cabinet SKU)
        domain = [('cabinet_sku', '=', selected_sku)]

        # Apply additional filters based on user selection
        if selected_countertop:
            domain.append(('counter_top_sku', '=', selected_countertop))
        else:
            # If counter_top_sku is not selected, set it to NULL for "cabinet only"
            if selected_mirror is None and selected_faucet is None:
                domain.append(('counter_top_sku', '=', None))

        if selected_mirror:
            domain.append(('mirror_sku', '=', selected_mirror))
        else:
            # If mirror_sku is not selected, set it to NULL
            if selected_faucet is None:
                domain.append(('mirror_sku', '=', None))

        if selected_faucet:
            domain.append(('faucet_sku', '=', selected_faucet))
        else:
            # If faucet_sku is not selected, set it to NULL
            if selected_mirror is None:
                domain.append(('faucet_sku', '=', None))

        # Search for the configuration that matches the criteria
        configured_kit = request.env['product.kits'].sudo().search(domain, limit=1)

        if configured_kit and configured_kit.product_sku:
            configured_product = request.env['product.product'].sudo().search(
                [('default_code', '=', configured_kit.product_sku)], limit=1
            )

        # If no configuration was found, set a flag for no available combination
        if not configured_kit:
            no_combination = True
        else:
            no_combination = False

        # Step 6: Find related kits (same color and collection)
        related_kits = []
        if configured_kit and configured_kit.color and configured_kit.collection:
            all_related_kits = request.env['product.kits'].sudo().search([
                ('id', '!=', configured_kit.id),
                ('color', '=', configured_kit.color),
                ('collection', '=', configured_kit.collection),
            ])

            seen_sizes = set()
            unique_related_kits = []
            for kit in all_related_kits:
                if kit.size and kit.size not in seen_sizes:
                    seen_sizes.add(kit.size)
                    unique_related_kits.append(kit)
            related_kits = unique_related_kits

        # Step 7: Fetch product specifications (template and variant attributes)
        product_specs = {}
        if configured_product:
            product_specs['variant_attributes'] = [{
                'attribute': val.attribute_id.name,
                'value': val.product_attribute_value_id.name,
            } for val in configured_product.product_template_attribute_value_ids]

            tmpl = configured_product.product_tmpl_id
            product_specs['template_attributes'] = [{
                'attribute': line.attribute_id.name,
                'values': [v.name for v in line.value_ids],
            } for line in tmpl.attribute_line_ids]

            product_specs['description_sale'] = tmpl.description_sale
            product_specs['description'] = tmpl.description
            product_specs['x_specifications'] = tmpl.x_specifications if hasattr(tmpl, 'x_specifications') else ''

        # Final Render
        return request.render('product_configuration.template_product_configuration', {
            'collections': unique_collections,
            'selected_collection': selected_collection,
            'colors': distinct_colors,
            'selected_color': selected_color,
            'selected_sku': selected_sku,
            'selected_countertop': selected_countertop,
            'selected_mirror': selected_mirror,
            'selected_faucet': selected_faucet,
            'size_cards': size_cards,
            'counter_top_cards': counter_top_cards,
            'mirror_cards': mirror_cards,
            'faucet_cards': faucet_cards,
            'configured_product': configured_product,
            'configured_kit': configured_kit,
            'related_kits': related_kits,
            'product_specs': product_specs,  # Pass product specs to the template
        })
