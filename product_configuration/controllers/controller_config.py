from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        selected_collection = kwargs.get('collection')
        selected_color = kwargs.get('color')  # New for selected color
        selected_sku = kwargs.get('cabinet_sku')
        selected_countertop = kwargs.get('counter_top_sku')
        selected_mirror = kwargs.get('mirror_sku')
        selected_faucet = kwargs.get('faucet_sku')

        # Fetch all unique collections to populate dropdown
        collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        unique_collections = sorted(list(set(collections)))

        if selected_collection:
            kits = request.env['product.kits'].sudo().search([('collection', '=', selected_collection)])
        else:
            kits = request.env['product.kits'].sudo().search([])

        # Get colors for selected collection
        colors = []
        if selected_collection:
            seen_colors = set()
            for kit in kits:
                color_val = getattr(kit, 'color', False) or getattr(kit, 'color_sku', False)  # Adjust field as needed
                if color_val and color_val not in seen_colors:
                    seen_colors.add(color_val)
                    colors.append(color_val)
            colors.sort()

        size_cards = []
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []

        seen_sizes = set()
        seen_countertops = set()
        seen_mirrors = set()
        seen_faucets = set()

        # Filter kits by color if selected
        if selected_color:
            kits = [kit for kit in kits if getattr(kit, 'color', False) == selected_color or getattr(kit, 'color_sku', False) == selected_color]

        # Prepare size cards
        for kit in kits:
            size = kit.size
            cabinet_sku = kit.cabinet_sku
            if size not in seen_sizes:
                seen_sizes.add(size)
                product = request.env['product.product'].sudo().search([('default_code', '=', cabinet_sku)], limit=1)
                size_cards.append({
                    'size': size,
                    'cabinet_sku': cabinet_sku,
                    'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                })

        size_cards.sort(key=lambda x: float(x['size']))

        if selected_sku:
            filtered_kits = [kit for kit in kits if kit.cabinet_sku == selected_sku]

            for kit in filtered_kits:
                # Countertop
                countertop_sku = kit.counter_top_sku
                if countertop_sku and countertop_sku not in seen_countertops:
                    seen_countertops.add(countertop_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', countertop_sku)], limit=1)
                    counter_top_cards.append({
                        'counter_top_sku': countertop_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

                # Mirror
                mirror_sku = kit.mirror_sku
                if mirror_sku and mirror_sku not in seen_mirrors:
                    seen_mirrors.add(mirror_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', mirror_sku)], limit=1)
                    mirror_cards.append({
                        'mirror_sku': mirror_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

                # Faucet
                faucet_sku = kit.faucet_sku
                if faucet_sku and faucet_sku not in seen_faucets:
                    seen_faucets.add(faucet_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', faucet_sku)], limit=1)
                    faucet_cards.append({
                        'faucet_sku': faucet_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })
                    
                # Determine final configured kit based on all selected components
                configured_kit = None
                if selected_sku and selected_countertop and selected_mirror and selected_faucet:
                    configured_kit = request.env['product.kits'].sudo().search([
                        ('cabinet_sku', '=', selected_sku),
                        ('counter_top_sku', '=', selected_countertop),
                        ('mirror_sku', '=', selected_mirror),
                        ('faucet_sku', '=', selected_faucet),
                    ], limit=1)
                elif selected_sku and selected_countertop and selected_mirror:
                    configured_kit = request.env['product.kits'].sudo().search([
                        ('cabinet_sku', '=', selected_sku),
                        ('counter_top_sku', '=', selected_countertop),
                        ('mirror_sku', '=', selected_mirror),
                    ], limit=1)
                elif selected_sku and selected_countertop:
                    configured_kit = request.env['product.kits'].sudo().search([
                        ('cabinet_sku', '=', selected_sku),
                        ('counter_top_sku', '=', selected_countertop),
                    ], limit=1)
                elif selected_sku:
                    configured_kit = request.env['product.kits'].sudo().search([
                        ('cabinet_sku', '=', selected_sku),
                    ], limit=1)

                # Try to find a product with the resulting product_sku
                configured_product = None
                if configured_kit and configured_kit.product_sku:
                    configured_product = request.env['product.product'].sudo().search([
                        ('default_code', '=', configured_kit.product_sku)
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
