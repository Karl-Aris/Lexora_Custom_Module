from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        selected_sku = kwargs.get('cabinet_sku')
        selected_countertop = kwargs.get('counter_top_sku')
        selected_mirror = kwargs.get('mirror_sku')
        selected_faucet = kwargs.get('faucet_sku')

        if not collection:
            return request.not_found()

        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        size_cards = []
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []


        seen_sizes = set()
        seen_countertops = set()
        seen_mirrors = set()
        seen_faucets = set()

        # Prepare size cards (always)
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

        size_cards.sort(key=lambda x: float(x['size']))  # Sort sizes

        # Prepare countertop cards only if a size is selected
        if selected_sku:
            # Filter kits to those matching selected size SKU
            filtered_kits = [kit for kit in kits if kit.cabinet_sku == selected_sku]

            # Load countertop
            for kit in filtered_kits:
                countertop_sku = kit.counter_top_sku
                if countertop_sku and countertop_sku not in seen_countertops:
                    seen_countertops.add(countertop_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', countertop_sku)], limit=1)
                    counter_top_cards.append({
                        'counter_top_sku': countertop_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })
            # Load mirrors
            for kit in filtered_kits:
                mirror_sku = kit.mirror_sku
                if mirror_sku and mirror_sku not in seen_mirrors:
                    seen_mirrors.add(mirror_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', mirror_sku)], limit=1)
                    mirror_cards.append({
                        'mirror_sku': mirror_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })
                    
             # Load faucets
            for kit in filtered_kits:
                faucet_sku = kit.faucet_sku
                if faucet_sku and faucet_sku not in seen_faucets:
                    seen_faucets.add(faucet_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', faucet_sku)], limit=1)
                    faucet_cards.append({
                        'faucet_sku': faucet_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'selected_sku': selected_sku,
            'selected_countertop': selected_countertop,
            'selected_mirror': selected_mirror,
            'selected_faucet': selected_faucet,
            'size_cards': size_cards,
            'counter_top_cards': counter_top_cards,
            'mirror_cards': mirror_cards,
            'faucet_cards': faucet_cards,
        })
