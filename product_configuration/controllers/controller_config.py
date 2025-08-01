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
        selected_size = kwargs.get('size')

        configured_kit = None
        configured_product = None

        # Load collections
        collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        unique_collections = sorted(set(collections))

        kits = request.env['product.kits'].sudo().search([])
        if selected_collection:
            kits = kits.filtered(lambda k: k.collection == selected_collection)

        # Get colors from kits under selected collection
        colors = sorted(set(kit.color.strip().lower() for kit in kits if kit.color))

        # Make sure to retain the original case of colors
        distinct_colors = []
        seen_colors = set()

        for color in colors:
            original_color = next((kit.color for kit in kits if kit.color.strip().lower() == color), None)
            if original_color and original_color.lower() not in seen_colors:
                distinct_colors.append(original_color)
                seen_colors.add(original_color.lower())
                
        # Normalize selected color to lowercase (same as before)        
        selected_color_normalized = selected_color.lower() if selected_color else None

        # Filter kits by the normalized color
        if selected_color:
            kits = kits.filtered(lambda k: k.color and k.color.lower() == selected_color_normalized)

        # Collect unique cabinet sizes/cards, ensuring no case sensitivity issues
        seen_sizes = set()
        size_cards = []

        for kit in kits:
            # Normalize the size (to avoid issues with case or extra spaces)
            if kit.size and kit.size.strip().lower() not in seen_sizes:
                seen_sizes.add(kit.size.strip().lower())
                
                product = request.env['product.product'].sudo().search([('default_code', '=', kit.cabinet_sku)], limit=1)
                size_cards.append({
                    'size': kit.size,
                    'cabinet_sku': kit.cabinet_sku,
                    'name': product.name,
                    'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                })

        # Sort the sizes
        size_cards.sort(key=lambda x: float(x['size']))

        # If cabinet_sku is selected, show options only for compatible kits
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []
        if selected_sku and selected_size:
            matching_kits = kits.filtered(lambda k: k.cabinet_sku == selected_sku and k.size == selected_size)

            # Collect unique countertop, mirror, faucet
            seen_ctops, seen_mirrors, seen_faucets = set(), set(), set()
            for kit in matching_kits:
                if kit.counter_top_sku and kit.counter_top_sku not in seen_ctops:
                    seen_ctops.add(kit.counter_top_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.counter_top_sku)], limit=1)
                    counter_top_cards.append({
                        'counter_top_sku': kit.counter_top_sku,
                        'name': prod.name,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })

                if kit.mirror_sku and kit.mirror_sku not in seen_mirrors:
                    seen_mirrors.add(kit.mirror_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.mirror_sku)], limit=1)
                    mirror_cards.append({
                        'mirror_sku': kit.mirror_sku,
                        'name': prod.name,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })

                if kit.faucet_sku and kit.faucet_sku not in seen_faucets:
                    seen_faucets.add(kit.faucet_sku)
                    prod = request.env['product.product'].sudo().search([('default_code', '=', kit.faucet_sku)], limit=1)
                    faucet_cards.append({
                        'faucet_sku': kit.faucet_sku,
                        'name': prod.name,
                        'image': prod.image_1920.decode('utf-8') if prod and prod.image_1920 else None
                    })
                    
       
                
        # Determine configured kit (only if >1 component selected)
        domain = [('cabinet_sku', '=', selected_sku)]
        domain.append(('size', '=', selected_size))
        domain.append(('counter_top_sku', '=', selected_countertop or ''))
        domain.append(('mirror_sku', '=', selected_mirror or ''))
        domain.append(('faucet_sku', '=', selected_faucet or ''))

        # Only search if more than just cabinet_sku is selected
        # if selected_sku and (selected_countertop or selected_mirror or selected_faucet):
        configured_kit = request.env['product.kits'].sudo().search(domain, limit=1)
        if configured_kit and configured_kit.product_sku:
            configured_product = request.env['product.product'].sudo().search(
                [('default_code', '=', configured_kit.product_sku)], limit=1
            )
            
        # Fetch the current partner's pricelist (property_product_pricelist)
        partner = request.env.user.partner_id  # Assuming the current logged-in user's partner
        pricelist = partner.property_product_pricelist  # This is the 'Tier 3 (USD)' pricelist
        
        fixed_price = None
        
        if pricelist:
            # Now fetch all the pricelist items that are related to the current product SKU
            pricelist_items = pricelist.item_ids  # Get all items from the pricelist

            # Iterate through the pricelist items
            for item in pricelist_items:
                # Check if the product SKU matches the SKU (ABC123, for example)
                product = item.product_tmpl_id  # The product template related to this item
                
                # Check if this product matches the SKU
                if configured_kit.product_sku == product.default_code:  # Check against the configured SKU
                    fixed_price = f"{pricelist.currency_id.symbol} {item.fixed_price}"
                    print(f"Found matching price rule for SKU {configured_kit.product_sku} in Pricelist {pricelist.name}:")
                    print(f"Product: {product.name}")
                    print(f"Price: {item.fixed_price} {pricelist.currency_id.symbol}")
                else:
                    print(f"No matching SKU found in this price rule: {item.name}")
        else:
            print("No pricelist found for the partner.")
            

        return request.render('product_configuration.template_product_configuration', {
            'collections': unique_collections,
            'selected_collection': selected_collection,
            'colors': colors,
            'selected_color': selected_color,
            'selected_sku': selected_sku,
            'selected_size': selected_size,
            'selected_countertop': selected_countertop,
            'selected_mirror': selected_mirror,
            'selected_faucet': selected_faucet,
            'size_cards': size_cards,
            'counter_top_cards': counter_top_cards,
            'mirror_cards': mirror_cards,
            'faucet_cards': faucet_cards,
            'configured_product': configured_product,
            'configured_kit': configured_kit,
            'fixed_price': fixed_price,
            'pricelist': pricelist,
        })
