from odoo.addons.website_sale.controllers.main import WebsiteSale, QueryURL

class WebsiteSaleStockFilter(WebsiteSale):
    @http.route(['/shop'], type='http', auth="public", website=True, sitemap=True)
    def shop(self, page=0, category=None, search='', **post):
        response = super().shop(page=page, category=category, search=search, **post)

        availability = post.get('availability')
        products = response.qcontext.get('products')
        if products and availability:
            if availability == 'available':
                products = products.filtered(lambda p: p.qty_available > 0)
            elif availability == 'not_available':
                products = products.filtered(lambda p: p.qty_available <= 0)
            response.qcontext['products'] = products

            # Update pager with new product count
            response.qcontext['pager']['total'] = len(products)

        return response
