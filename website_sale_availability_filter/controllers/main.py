from odoo import http
from odoo.http import request

class WebsiteSale(http.Controller):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, **kwargs):
        domain = []

        # Product Availability filtering logic
        availability = kwargs.get('availability')
        if availability:
            location = request.env.ref('stock.stock_location_stock')  # Change if needed
            product_ids_with_stock = request.env['stock.quant'].sudo().read_group(
                [('location_id', '=', location.id)],
                ['product_id', 'quantity:sum'],
                ['product_id']
            )
            in_stock_product_ids = [res['product_id'][0] for res in product_ids_with_stock if res['quantity'] > 0]

            if availability == 'available':
                domain += [('id', 'in', in_stock_product_ids)]
            elif availability == 'not_available':
                domain += [('id', 'not in', in_stock_product_ids)]

        # continue with your normal shop product search logic
        products = request.env['product.template'].sudo().search(domain)

        return request.render("website_sale.products", {
            'products': products,
        })
