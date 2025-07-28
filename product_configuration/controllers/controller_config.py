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

        # Load collections
        collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        unique_collections = sorted(set(collections))

        kits = request.env['product.kits'].sudo().search([])
        if selected_collection:
            kits = kits.filtered(lambda k: k.collection == selected_collection)

        # Get colors from kits under selected collection
        colors = sorted(set(kit.color for kit in kits if kit.color))

        # Filter by color if selected
        if selected_color:
            kits = kits.filtered(lambda k: k.color == selected_color)

        # Collect unique cabinet sizes/cards
        seen_sizes = set()
        size_cards = []
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

        # If cabinet_sku is selected, show options only for compatible kits
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []
        if selected_sku:
            matching_kits = kits.filtered(lambda k: k.cabinet_sku == selected_sku)

            # Collect unique countertop, mirror, faucet
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

        # Determine configured kit (only if >1 component selected)
        # Start with the base domain using the cabinet_sku
        domain = [('cabinet_sku', '=', selected_sku)]

        # Check the conditions based on the selected components
        if selected_countertop and not selected_mirror and not selected_faucet:
            # Show cabinet + countertop only
            domain.append(('counter_top_sku', '=', selected_countertop))

        elif selected_countertop and selected_mirror and not selected_faucet:
            # Show cabinet + countertop + mirror
            domain.append(('counter_top_sku', '=', selected_countertop))
            domain.append(('mirror_sku', '=', selected_mirror))

        elif selected_countertop and not selected_mirror and selected_faucet:
            # Show cabinet + countertop + faucet
            domain.append(('counter_top_sku', '=', selected_countertop))
            domain.append(('faucet_sku', '=', selected_faucet))

        elif selected_countertop and selected_mirror and selected_faucet:
            # Show cabinet + countertop + mirror + faucet
            domain.append(('counter_top_sku', '=', selected_countertop))
            domain.append(('mirror_sku', '=', selected_mirror))
            domain.append(('faucet_sku', '=', selected_faucet))

        # If only cabinet_sku is selected, don't add any other components (countertop, mirror, faucet)
        elif selected_sku and not selected_countertop and not selected_mirror and not selected_faucet:
            # Just the cabinet product
            pass

        # Perform the search with the updated domain
        if selected_sku:
            # Search for kits first with the exact cabinet_sku and selected components
            configured_kit = request.env['product.kits'].sudo().search(domain, limit=1)

            # Check if a matching kit is found, and if it has a valid product_sku
            if configured_kit and configured_kit.product_sku:
                configured_product = request.env['product.product'].sudo().search(
                    [('default_code', '=', configured_kit.product_sku)], limit=1
                )

            # If no kit is found, check the individual cabinet product
            if not configured_kit:
                # If no kit is found, return the product that matches the selected cabinet_sku directly
                configured_product = request.env['product.product'].sudo().search(
                    [('default_code', '=', selected_sku)], limit=1
                )

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
