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

        # Initialize empty for safety
        configured_kit = None
        configured_product = None

        # Get unique collections
        collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        unique_collections = sorted(list(set(collections)))

        # Get all kits based on selected collection
        kits = request.env['product.kits'].sudo().search(
            [('collection', '=', selected_collection)] if selected_collection else []
        )

        # Extract available colors
        colors = []
        if selected_collection:
            seen_colors = set()
            for kit in kits:
                color_val = getattr(kit, 'color', False) or getattr(kit, 'color_sku', False)
                if color_val and color_val not in seen_colors:
                    seen_colors.add(color_val)
                    colors.append(color_val)
            colors.sort()

        # Filter kits by color if selected
        if selected_color:
            kits = [kit for kit in kits if kit.color == selected_color or kit.color_sku == selected_color]

        # Build size cards
        size_cards = []
        seen_sizes = set()
        for kit in kits:
            if kit.size not in seen_sizes:
                seen_sizes.add(kit.size)
                product = request.env['product.product'].sudo().search([('default_code', '=', kit.cabinet_sku)], limit=1)
                size_cards.append({
                    'size': kit.size,
                    'cabinet_sku': kit.cabinet_sku,
                    'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                })
        size_cards.sort(key=lambda x: float(x['size']))

        # Cards for countertop, mirror, faucet
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []

        seen_countertops = set()
        seen_mirrors = set()
        seen_faucets = set()

        if selected_sku:
            filtered_kits = [kit for kit in kits if kit.cabinet_sku == selected_sku]

            for kit in filtered_kits:
                # Countertops
                if kit.counter_top_sku and kit.counter_top_sku not in seen_countertops:
                    seen_countertops.add(kit.counter_top_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', kit.counter_top_sku)], limit=1)
                    counter_top_cards.append({
                        'counter_top_sku': kit.counter_top_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

                # Mirrors
                if kit.mirror_sku and kit.mirror_sku not in seen_mirrors:
                    seen_mirrors.add(kit.mirror_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', kit.mirror_sku)], limit=1)
                    mirror_cards.append({
                        'mirror_sku': kit.mirror_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

                # Faucets
                if kit.faucet_sku and kit.faucet_sku not in seen_faucets:
                    seen_faucets.add(kit.faucet_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', kit.faucet_sku)], limit=1)
                    faucet_cards.append({
                        'faucet_sku': kit.faucet_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

        # Compute configured kit and fallback image
        if selected_sku:
            domain = [('cabinet_sku', '=', selected_sku)]
            if selected_countertop:
                domain.append(('counter_top_sku', '=', selected_countertop))
            if selected_mirror:
                domain.append(('mirror_sku', '=', selected_mirror))
            if selected_faucet:
                domain.append(('faucet_sku', '=', selected_faucet))

            configured_kit = request.env['product.kits'].sudo().search(domain, limit=1)

            if configured_kit and configured_kit.product_sku:
                configured_product = request.env['product.product'].sudo().search([
                    ('default_code', '=', configured_kit.product_sku)
                ], limit=1)
            else:
                # Fallback to just the cabinet product if no valid combination
                configured_product = request.env['product.product'].sudo().search([
                    ('default_code', '=', selected_sku)
                ], limit=1)

        return request.render('product_configuration.template_product_configuration', {
            'collections': unique_collections,
            'selected_collection': selected_collection,
            'colors': colors,
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
        })
