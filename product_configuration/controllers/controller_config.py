from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductConfigurationController(http.Controller):

    @http.route('/store', type='http', auth='public', website=True)
    def store(self, **kwargs):
        collection = kwargs.get('collection')
        selected_sku = kwargs.get('cabinet_sku')
        selected_countertop_sku = kwargs.get('counter_top_sku')

        if not collection:
            return "Collection parameter is required"

        kits = request.env['product.kits'].sudo().search([('collection', '=', collection)])

        # Prepare size cards grouped by size
        size_cards = []
        seen_sizes = set()
        sku_to_size = {}  # map cabinet_sku to size for filtering countertops later

        for kit in kits:
            size = kit.size
            cabinet_sku = kit.cabinet_sku
            if size not in seen_sizes:
                seen_sizes.add(size)
            sku_to_size[cabinet_sku] = size

        # Sort sizes low to high
        sorted_sizes = sorted(seen_sizes)

        # Build size cards list with images for each cabinet_sku that matches size
        size_cards = []
        processed_skus = set()
        for size in sorted_sizes:
            # find all kits with this size, but only add one card per cabinet_sku
            kits_with_size = [k for k in kits if k.size == size]
            for kit in kits_with_size:
                cabinet_sku = kit.cabinet_sku
                if cabinet_sku not in processed_skus:
                    processed_skus.add(cabinet_sku)
                    product = request.env['product.product'].sudo().search([('default_code', '=', cabinet_sku)], limit=1)
                    size_cards.append({
                        'size': size,
                        'cabinet_sku': cabinet_sku,
                        'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                    })

        # Find the selected cabinet size to filter countertops
        selected_size = None
        if selected_sku:
            selected_size = sku_to_size.get(selected_sku)

        # Prepare countertop cards filtered by selected cabinet size
        counter_top_cards = []
        seen_countertops = set()
        for kit in kits:
            # Skip if selected size does not match kit size (filter countertops)
            if selected_size and kit.size != selected_size:
                continue

            counter_top_sku = kit.counter_top_sku
            if counter_top_sku and counter_top_sku not in seen_countertops:
                seen_countertops.add(counter_top_sku)
                product = request.env['product.product'].sudo().search([('default_code', '=', counter_top_sku)], limit=1)
                counter_top_cards.append({
                    'counter_top_sku': counter_top_sku,
                    'image': product.image_1920.decode('utf-8') if product and product.image_1920 else None,
                })

        return request.render('product_configuration.template_product_configuration', {
            'collection': collection,
            'size_cards': size_cards,
            'selected_sku': selected_sku,
            'counter_top_cards': counter_top_cards,
            'selected_countertop_sku': selected_countertop_sku,
        })
