from odoo import http
from odoo.http import request

class ProductKitsController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store_by_collection(self, **kwargs):
        collection = kwargs.get('collection')
        selected_color = kwargs.get('color')
        selected_sku = kwargs.get('cabinet_sku')
        selected_countertop = kwargs.get('counter_top_sku')
        selected_mirror = kwargs.get('mirror_sku')
        selected_faucet = kwargs.get('faucet_sku')

        # Get all collections (for dropdown)
        all_collections = request.env['product.kits'].sudo().search([]).mapped('collection')
        all_collections = sorted(set(all_collections))

        color_tags = []
        size_cards = []
        counter_top_cards = []
        mirror_cards = []
        faucet_cards = []

        if collection:
            # Colors for the selected collection
            kits_in_collection = request.env['product.kits'].sudo().search([('collection', '=', collection)])
            seen_colors = set()
            for kit in kits_in_collection:
                if kit.color and kit.color not in seen_colors:
                    seen_colors.add(kit.color)
                    color_tags.append(kit.color)

            if selected_color:
                kits = kits_in_collection.filtered(lambda k: k.color == selected_color)

                seen_sizes = set()
                seen_countertops = set()
                seen_mirrors = set()
                seen_faucets = set()

                for kit in kits:
                    # Size cards
                    size = kit.size
                    cabinet_sku = kit.cabinet_sku
                    if size not in seen_sizes:
                        seen_sizes.add(size)
                        product = request.env['product.product'].sudo().search([('default_code', '=', cabinet_sku)], limit=1)
                        size_cards.append({
                            'size': size,
                            'cabinet_sku': cabinet_sku,
                            'image': product.image_1920.decode('utf-8') if product.image_1920 else None,
                        })

                    # Countertop cards
                    counter_sku = kit.counter_top_sku
                    if counter_sku and counter_sku not in seen_countertops:
                        seen_countertops.add(counter_sku)
                        product = request.env['product.product'].sudo().search([('default_code', '=', counter_sku)], limit=1)
                        counter_top_cards.append({
                            'counter_top_sku': counter_sku,
                            'image': product.image_1920.decode('utf-8') if product.image_1920 else None,
                        })

                    # Mirror cards
                    mirror_sku = kit.mirror_sku
                    if mirror_sku and mirror_sku not in seen_mirrors:
                        seen_mirrors.add(mirror_sku)
                        product = request.env['product.product'].sudo().search([('default_code', '=', mirror_sku)], limit=1)
                        mirror_cards.append({
                            'mirror_sku': mirror_sku,
                            'image': product.image_1920.decode('utf-8') if product.image_1920 else None,
                        })

                    # Faucet cards
                    faucet_sku = kit.faucet_sku
                    if faucet_sku and faucet_sku not in seen_faucets:
                        seen_faucets.add(faucet_sku)
                        product = request.env['product.product'].sudo().search([('default_code', '=', faucet_sku)], limit=1)
                        faucet_cards.append({
                            'faucet_sku': faucet_sku,
                            'image': product.image_1920.decode('utf-8') if product.image_1920 else None,
                        })

                size_cards.sort(key=lambda x: float(x['size']))

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'selected_color': selected_color,
            'selected_sku': selected_sku,
            'selected_countertop': selected_countertop,
            'selected_mirror': selected_mirror,
            'selected_faucet': selected_faucet,
            'all_collections': all_collections,
            'color_tags': color_tags,
            'size_cards': size_cards,
            'counter_top_cards': counter_top_cards,
            'mirror_cards': mirror_cards,
            'faucet_cards': faucet_cards,
        })
