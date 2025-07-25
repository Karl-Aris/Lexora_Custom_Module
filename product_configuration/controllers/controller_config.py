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

        # Collections
        all_collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        collections = sorted(set(all_collections))

        # Kits for selected collection
        kits = request.env['product.kits'].sudo().search(
            [('collection', '=', selected_collection)] if selected_collection else []
        )

        # Colors
        colors = []
        if selected_collection:
            seen = set()
            for k in kits:
                c = getattr(k, 'color', False)
                if c and c not in seen:
                    seen.add(c)
                    colors.append(c)
            colors.sort()

        # Filter kits by color
        if selected_color:
            kits = [k for k in kits if k.color == selected_color]

        # Prepare size cards
        size_cards = []
        seen_sizes = set()
        for k in kits:
            if k.size not in seen_sizes:
                seen_sizes.add(k.size)
                prod = request.env['product.product'].sudo().search([('default_code', '=', k.cabinet_sku)], limit=1)
                size_cards.append({
                    'size': k.size,
                    'cabinet_sku': k.cabinet_sku,
                    'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None,
                })
        size_cards.sort(key=lambda x: float(x['size']))

        # Countertop / Mirror / Faucet cards
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []
        seen_ct, seen_mr, seen_fa = set(), set(), set()

        if selected_sku:
            filtered = [k for k in kits if k.cabinet_sku == selected_sku]
            for k in filtered:
                if k.counter_top_sku and k.counter_top_sku not in seen_ct:
                    seen_ct.add(k.counter_top_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', k.counter_top_sku)], limit=1)
                    counter_top_cards.append({'counter_top_sku': k.counter_top_sku,
                                               'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None})
                if k.mirror_sku and k.mirror_sku not in seen_mr:
                    seen_mr.add(k.mirror_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', k.mirror_sku)], limit=1)
                    mirror_cards.append({'mirror_sku': k.mirror_sku,
                                         'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None})
                if k.faucet_sku and k.faucet_sku not in seen_fa:
                    seen_fa.add(k.faucet_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', k.faucet_sku)], limit=1)
                    faucet_cards.append({'faucet_sku': k.faucet_sku,
                                         'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None})

        # Determine configured kit only when all selected fields are not None
        component_count = sum(bool(x) for x in [selected_sku, selected_countertop, selected_mirror, selected_faucet])
        if component_count > 0 and selected_sku:
            domain = [('cabinet_sku', '=', selected_sku)]
            if selected_countertop: domain.append(('counter_top_sku', '=', selected_countertop))
            if selected_mirror: domain.append(('mirror_sku', '=', selected_mirror))
            if selected_faucet: domain.append(('faucet_sku', '=', selected_faucet))

            configured_kit = request.env['product.kits'].sudo().search(domain, limit=1)
            if configured_kit and configured_kit.product_sku:
                configured_product = request.env['product.product'].sudo().search(
                    [('default_code', '=', configured_kit.product_sku)], limit=1
                )
        # Fallback: just cabinet image if no combination found
        if not configured_product and selected_sku:
            configured_product = request.env['product.product'].sudo().search(
                [('default_code', '=', selected_sku)], limit=1
            )

        return request.render('product_configuration.template_product_configuration', {
            'collections': collections,
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
